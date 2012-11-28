#! /usr/bin/python
from sensors import *
from math import *
import numpy
from distributions import *
import sys
import pickle
# classify based on traces
class Classify(object) :

	''' Windowing primitives '''
	last_time=-1
	WINDOW_IN_MILLI_SECONDS=5000
	WINDOW_SHIFT_IN_MILLI_SECONDS=1000
	WINDOW_TEMPLATE_LENGTH=60 # 60 windowed variances
	current_window=[]
	current_variance_window=[]  # to accumulate variances over 1 minute

	activity_templates=[]	

	''' power stats for each phone '''
	power_accel=dict()
	power_wifi=dict()
	power_gps=dict()
	power_gsm=dict()
	power_nwk_loc=dict()

	def __init__(self,sim_phone,classifier_model,power_model) :
		self.sim_phone=sim_phone
		self.classifier_output=[]
		
		''' set initial sampling intervals in milliseconds '''
		execfile(power_model)
		self.current_sampling_interval=max(self.power_accel.keys())
		sim_phone.change_accel_interval(max(self.power_accel.keys()))
		sim_phone.change_wifi_interval(max(self.power_wifi.keys()))
		sim_phone.change_gps_interval(max(self.power_gps.keys()))
		sim_phone.change_gsm_interval(max(self.power_gsm.keys()))
		sim_phone.change_nwk_loc_interval(max(self.power_nwk_loc.keys()))
		
		classifier_model_handle=open(classifier_model,"r");
		self.activity_templates = pickle.load(classifier_model_handle);
		
	def predict_label(self, observation):
		gamma = 1
		posterior_prob = [sys.float_info.min]*5
		for i in range(5):
			dist = []
			for template in self.activity_templates[i]:
				assert (len(template)==len(observation))
				angle=numpy.dot(observation,template)/(numpy.linalg.norm(observation)*numpy.linalg.norm(template))
				dist.append(angle)
			posterior_prob[i] = numpy.sum([exp(-gamma * d) for d in dist])
		posterior_prob = map (lambda x : x / sum(posterior_prob),posterior_prob)
		return posterior_prob

	def mean_and_var(self,value_list) :
		if (value_list==[]) :
			return (None,None)
		meanSq=reduce(lambda acc,update : acc + update**2,value_list,0.0)/len(value_list)
		mean=reduce(lambda acc,update : acc + update,value_list,0.0)/len(value_list)
		return (mean,meanSq-mean*mean)

	def callback(self,sensor_reading,current_time) :
		''' Interface to simulator :  Leave final result as (timestamp,output_distribution) pairs in classifier_output '''
		if (isinstance(sensor_reading,Accel)) :
			''' compute accel magnitude and keep track of windows '''
			accel_mag=sqrt(sensor_reading.accel_x**2+sensor_reading.accel_y**2+sensor_reading.accel_z**2)
		        self.current_window=filter(lambda x : x[0] >=  current_time - self.WINDOW_IN_MILLI_SECONDS, self.current_window)
		        self.current_window+=[(current_time,accel_mag)]
			(_,variance)=self.mean_and_var(map(lambda x : x[1],self.current_window));
			self.last_time=current_time if self.last_time == -1 else self.last_time
			if (current_time - self.last_time)  >= self.WINDOW_SHIFT_IN_MILLI_SECONDS: 
				self.last_time = current_time
				self.current_variance_window += [variance]
			if ( len(self.current_variance_window) == self.WINDOW_TEMPLATE_LENGTH ) :
				posterior_prob = self.predict_label(self.current_variance_window)
				self.classifier_output.append((current_time, Distribution(5,posterior_prob)))
				self.current_variance_window=[]
				print "Posterior is ",posterior_prob
