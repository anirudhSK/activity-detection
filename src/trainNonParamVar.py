#! /usr/bin/python
# train based on traces
from sensors import *
from math import *
from numpy.fft import *
import numpy
from normal import *
import sys
import pickle
class  Train(object) :

	''' Windowing primitives '''
	last_time=-1
	WINDOW_IN_MILLI_SECONDS=5000
	WINDOW_SHIFT_IN_MILLI_SECONDS=1000
	WINDOW_TEMPLATE_LENGTH=60 # 60 windowed variances
	current_window=[]
	current_variance_window=[]  # to accumulate variances over 1 minute
	
	''' Data required for ML estimates for each label '''
	activity_templates = [[] for _ in range(5)]

	def __init__(self,sim_phone) :
		self.sim_phone=sim_phone
	
	def mean_and_var(self,value_list) :
		if (value_list==[]) :
			return (None,None)
		meanSq=reduce(lambda acc,update : acc + update**2,value_list,0.0)/len(value_list)
		mean=reduce(lambda acc,update : acc + update,value_list,0.0)/len(value_list)
		return (mean,meanSq-mean*mean)

	def callback(self,sensor_reading,current_time,gnd_truth) :
		if (isinstance(sensor_reading,Accel)) :
			''' compute accel magnitude and keep track of windows '''
			accel_mag=sqrt(sensor_reading.accel_x**2+sensor_reading.accel_y**2+sensor_reading.accel_z**2)
		        self.current_window=filter(lambda x : x[0] >=  current_time - self.WINDOW_IN_MILLI_SECONDS, self.current_window)
		        self.current_window+=[(current_time,accel_mag)]
			(_,variance)=self.mean_and_var(map(lambda x : x[1],self.current_window));
			self.last_time=current_time if self.last_time == -1 else self.last_time
			if (current_time - self.last_time)  >= self.WINDOW_SHIFT_IN_MILLI_SECONDS : 
				self.last_time = current_time
				self.current_variance_window += [variance]
			if ( len(self.current_variance_window) == self.WINDOW_TEMPLATE_LENGTH ) :
				self.activity_templates[gnd_truth] += [self.current_variance_window]
				self.current_variance_window=[]

	def output_classifer(self) :
		# make sure each activity has the same number of templates
		minimum_template_num = min(map(lambda x: len(x), self.activity_templates))
		for i in range(5):
			while len(self.activity_templates[i]) > minimum_template_num:
				self.activity_templates[i].pop(0)	
		fh=open("pickled.output","w")
		pickle.dump(self.activity_templates,fh);
