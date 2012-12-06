#! /usr/bin/python
# Indoor Outdoor classifier
from sensors import *
from math import *
from numpy.fft import *
import numpy
from normal import *
from distributions import *
import sys
import operator
# classify based on traces
class Classify(object) :
	''' Windowing primitives '''
	WINDOW_IN_MILLI_SECONDS=5000
	current_window=[]
	NUM_STATES=3
	''' Energy adapataion '''
	current_sampling_interval=1000

	''' power stats for each phone '''
	power_accel=dict()
	power_wifi=dict()
	power_gps=dict()
	power_gsm=dict()
	power_nwk_loc=dict()

	''' parameters of distributions used for Naive Bayes prediction '''
	avg_rssi_dist=[0]*NUM_STATES
	fraction_aps_dist=[0]*NUM_STATES

	def __init__(self,sim_phone,classifier_model,power_model) :
		self.sim_phone=sim_phone
		self.classifier_output=[]

		execfile(power_model)

		''' set initial sampling intervals to the max value in milliseconds '''
		self.current_sampling_interval=max(self.power_wifi.keys())
		sim_phone.change_accel_interval(max(self.power_accel.keys()))
		sim_phone.change_wifi_interval(max(self.power_wifi.keys()))
		sim_phone.change_gps_interval(max(self.power_gps.keys()))
		sim_phone.change_gsm_interval(max(self.power_gsm.keys()))
		sim_phone.change_nwk_loc_interval(max(self.power_nwk_loc.keys()))

		execfile(classifier_model)
		
	def predict_label(self,average_rssi,fraction_aps) :
		''' Predict the label given the average_rssi, fraction_aps '''
		likelihood=[sys.float_info.min]*self.NUM_STATES
		for label in range(0,len(likelihood)) :
			likelihood[label] += (self.avg_rssi_dist[label].pdf(average_rssi))   * (self.fraction_aps_dist[label].pdf(fraction_aps)) 
		posterior_pmf=[0]*len(likelihood)
		for label in range(0,len(likelihood)) :
			posterior_pmf[label]=likelihood[label]/sum(likelihood)
		return	Distribution(len(likelihood),posterior_pmf)

	def callback(self,sensor_reading,current_time) :
		''' Interface to simulator :  Leave final result as (timestamp,output_distribution) pairs in classifier_output '''
		if (isinstance(sensor_reading,WiFi)) :
			# slide window 
			# zip aps and rssis into one list
			ap_rssis=zip(sensor_reading.ap_list,sensor_reading.rssi_list);
			self.current_window+=[(sensor_reading.time_stamp,ap_rssis)]
			self.current_window=filter(lambda x : x[0] >=  current_time - self.WINDOW_IN_MILLI_SECONDS,self.current_window)
			# calc. num of aps in window :
			aps_seen=reduce(lambda acc,update : acc + len(update[1]),self.current_window,0)
		
			# calc. num of aps in window above threshold :
			threshold=-80
			good_ap_window=[]
			for sample in self.current_window :
				ts=sample[0]
				aps=sample[1]
				good_aps= filter(lambda x : x[1] > threshold,aps);
				good_ap_window+=[(ts,good_aps)]
			good_aps_seen=reduce(lambda acc,update : acc + len(update[1]),good_ap_window,0)
		
			# calculate average over sliding window :
			sum_window_rssi=0
			for sample in self.current_window :
				ts=sample[0]
				aps=sample[1]
				sum_window_rssi+= reduce(lambda acc,update : acc + update[1] ,aps ,0);
			avg_window_rssi=sum_window_rssi/aps_seen;

			posterior_dist=self.predict_label(avg_window_rssi,(good_aps_seen*1.0)/aps_seen)
			self.classifier_output.append((current_time,posterior_dist))
			
			#self.energy_adapt(current_time, self.power_accel, [0,1,2], posterior_dist.pmf)
	def energy_adapt (self, current_time, power_accel, callback_list, posterior_pmf) :
			print "Current sampling interval is ",self.current_sampling_interval
			# check if you can ramp up at all
			do_i_ramp_up=reduce(lambda acc, update : acc or (posterior_pmf[update] >= 0.4), callback_list ,False); 
			if (do_i_ramp_up) :
				try :
					self.current_sampling_interval=max(filter(lambda x : x < self.current_sampling_interval, self.power_wifi.keys()))
				except Exception :
					self.current_sampling_interval=self.current_sampling_interval
				self.sim_phone.change_wifi_interval(self.current_sampling_interval)
				return