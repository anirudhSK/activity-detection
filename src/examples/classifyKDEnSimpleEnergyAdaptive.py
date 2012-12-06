#! /usr/bin/python
from sensors import *
from math import *
from numpy.fft import *
import numpy
from normal import *
from distributions import *
import sys
import operator
import pickle
from scipy.stats.kde import gaussian_kde
from scipy.stats import norm
#import matplotlib
# classify based on traces
class KernelSimpleEnergyClassify(object) :
	''' Windowing primitives '''
	WINDOW_IN_MILLI_SECONDS=5000
	WIFI_WINDOW_IN_MILLI_SECONDS= (3 * 60 * 1000)
	
	current_window=[]
	current_wifi_obs=[]
	must_be_driving = 0
	must_be_static = 0
	last_print_out = -1
	wifi_prev_time = -1

	last_energy_update = 0
	activity_templates=[]	
	recs = dict()

	''' power stats for each phone '''
	power_accel=dict()
	power_wifi=dict()
	power_gps=dict()
	power_gsm=dict()
	power_nwk_loc=dict()
	energy_consumed=0
	current_sampling_interval = 1000

	feature_list = []
	kernel_function = dict()
	callback_list = []
	#Viterbi
	#stateScore = [0]*5
	prev_prediction = -1
	#EWMA
	ewma_window = []
	def __init__(self,sim_phone,classifier_model,power_model,callback_list) :
		self.sim_phone=sim_phone
		self.classifier_output=[]
		self.callback_list = callback_list
		self.ewma_window = [0.2]*5
		''' set initial sampling intervals in milliseconds '''
		execfile(power_model)
		
		self.current_sampling_interval=max(self.power_accel.keys())
		sim_phone.change_accel_interval(max(self.power_accel.keys()))
		sim_phone.change_wifi_interval(max(self.power_wifi.keys()))
		sim_phone.change_gps_interval(max(self.power_gps.keys()))
		sim_phone.change_gsm_interval(max(self.power_gsm.keys()))
		sim_phone.change_nwk_loc_interval(max(self.power_nwk_loc.keys()))
		
		classifier_model_handle=open(classifier_model,"r");
		self.feature_list = pickle.load(classifier_model_handle);

		for i in range(5):
			self.kernel_function[i] = []
			for j in range(len(self.feature_list[i])):
				kernel_pdf = gaussian_kde(self.feature_list[i][j])
				#kernel_pdf.covariance_factor = lambda : 0.
				#kernel_pdf._compute_covariance()
				self.kernel_function[i] += [kernel_pdf]
		self.feature_list = []


	def mean_and_var(self,value_list) :
		if (value_list==[]) :
			return (None,None)
		meanSq=reduce(lambda acc,update : acc + update**2,value_list,0.0)/len(value_list)
		mean=reduce(lambda acc,update : acc + update,value_list,0.0)/len(value_list)
		return (mean,meanSq-mean*mean)

	def predict_label_with_wifi_hint(self, mean_fv, sigma_fv, peak_freq_fv, strength_var_fv, must_be_driving, must_be_static):
		''' Predict the label given the mean, sigma, peak frequency and strength variation components of the feature vector '''
		likelihood=[sys.float_info.min]*5
		for label in range(0,5) :
			likelihood[label] += (self.kernel_function[label][0].evaluate(mean_fv)[0]) * (self.kernel_function[label][1].evaluate(sigma_fv)[0]) *(self.kernel_function[label][2].evaluate(peak_freq_fv)[0]) * (self.kernel_function[label][3].evaluate(strength_var_fv)[0])
		posterior_pmf=[0]*5

		if must_be_static:
			posterior_pmf[0] = 1
			return	Distribution(5,posterior_pmf)

		elif must_be_driving:
			posterior_pmf[4] = 1
			return	Distribution(5,posterior_pmf)

		else:
			for label in range(0,5):
			
				if sum(likelihood) > 0:
					posterior_pmf[label]=likelihood[label]/sum(likelihood)
				else:
					posterior_pmf[label] = 0.2

			return	Distribution(5,posterior_pmf)

	def predict_label(self,mean_fv,sigma_fv,peak_freq_fv,strength_var_fv) :
		''' Predict the label given the mean, sigma, peak frequency and strength variation components of the feature vector '''
		likelihood=[sys.float_info.min]*5
		for label in range(0,5) :
			likelihood[label] += (self.kernel_function[label][0].evaluate(mean_fv)[0]) * (self.kernel_function[label][1].evaluate(sigma_fv)[0]) *(self.kernel_function[label][2].evaluate(peak_freq_fv)[0]) * (self.kernel_function[label][3].evaluate(strength_var_fv)[0])
		posterior_pmf=[0]*5
		for label in range(0,5) :
			if sum(likelihood) > 0:
				posterior_pmf[label]=likelihood[label]/sum(likelihood)
			else:
				posterior_pmf[label] = 0.2
		return	Distribution(5,posterior_pmf)

	def get_wifi_fingerprint_dist(self, set_of_wifi_obs):
		matrix_list = []
		for i in range(len(set_of_wifi_obs)-1):
			cur_wifi_ob = set_of_wifi_obs[i]
			nxt_wifi_ob= set_of_wifi_obs[i+1]
			
			cur_wifi_bit = [0]*len(cur_wifi_ob.ap_list)
			nxt_wifi_bit = [0]*len(nxt_wifi_ob.ap_list)
			
			pair_dist = 0
			intersect_num = 0
			for j in range(len(cur_wifi_ob.ap_list)):
				for k in range(len(nxt_wifi_ob.ap_list)):
					if cur_wifi_ob.ap_list[j].find(nxt_wifi_ob.ap_list[k]) >= 0:
						cur_wifi_bit[j] = 1
						nxt_wifi_bit[k] = 1
						pair_dist += (cur_wifi_ob.rssi_list[j] - nxt_wifi_ob.rssi_list[k])* (cur_wifi_ob.rssi_list[j] - nxt_wifi_ob.rssi_list[k])
						intersect_num += 1
						break

			for j in range(len(cur_wifi_ob.ap_list)):
				if (cur_wifi_bit[j] == 0):
					pair_dist += (cur_wifi_ob.rssi_list[j] * cur_wifi_ob.rssi_list[j])

			for k in range(len(nxt_wifi_ob.ap_list)):
				if (nxt_wifi_bit[k] == 0):
					pair_dist += (nxt_wifi_ob.rssi_list[k] * nxt_wifi_ob.rssi_list[k])

			pair_dist = sqrt(pair_dist)
			union_num = len(cur_wifi_ob.ap_list) + len(nxt_wifi_ob.ap_list) - intersect_num
			matrix = 0
			if union_num > 0:
				matrix = 99 * (intersect_num/(union_num*1.0)) + ( 99 - (pair_dist/(union_num *1.0)))

			matrix_list.append(matrix)	
		
		return self.mean_and_var(matrix_list)

	def callback(self,sensor_reading,current_time) :
		''' Interface to simulator :  Leave final result as (timestamp,output_distribution) pairs in classifier_output '''
		#if (isinstance(sensor_reading,GSM)):
		#	self.current_gsm_obs= filter(lambda x: x.time_stamp >= current_time - self.GSM_WINDOW_IN_MILLI_SECONDS ,self.current_gsm_obs)
		#	print self.current_gsm_obs	
		#	if len(sensor_reading.ap_list) > 0:
		#		self.current_wifi_obs+=[sensor_reading]	
			
		#	if len(self.current_wifi_obs) > 0: ## a window of wifi fingerprints
		#		print "current_time", current_time , self.current_wifi_obs
		#		(wifi_matrix_mean, wifi_matrix_var) = self.get_wifi_fingerprint_dist(self.current_wifi_obs)
				#averaged_ap_num = sum(map(lambda x : len(x.ap_list), self.current_wifi_obs))/len(self.current_wifi_obs)
				#averaged_max_rssi = sum(map(lambda x : max(x.rssi_list),self.current_wifi_obs))/len(self.current_wifi_obs)
				
				#print "averaged_ap_num", averaged_ap_num, "averaged_max_rssi", averaged_max_rssi
				#if averaged_ap_num >= 10 and averaged_max_rssi > -80:
				#	self.might_be_driving = 0	
				#else:
				#	self.might_be_driving = 1
		#		print wifi_matrix_mean
		#		if wifi_matrix_mean > 115:
		#			self.must_be_static = 1
		#		else:
		#			self.must_be_static = 0

		#		if wifi_matrix_mean < 70 and len(self.current_wifi_obs) > 0:
		#			self.must_be_driving = 1
		#		else:
		#			self.must_be_driving = 0

		if (isinstance(sensor_reading,WiFi)):
			self.current_wifi_obs= filter(lambda x: x.time_stamp >= current_time - self.WIFI_WINDOW_IN_MILLI_SECONDS ,self.current_wifi_obs)
			print self.current_wifi_obs	
			if len(sensor_reading.ap_list) > 0:
				self.current_wifi_obs+=[sensor_reading]	
			
			if len(self.current_wifi_obs) > 0: ## a window of wifi fingerprints
				print "current_time", current_time , self.current_wifi_obs
				(wifi_matrix_mean, wifi_matrix_var) = self.get_wifi_fingerprint_dist(self.current_wifi_obs)
				#averaged_ap_num = sum(map(lambda x : len(x.ap_list), self.current_wifi_obs))/len(self.current_wifi_obs)
				#averaged_max_rssi = sum(map(lambda x : max(x.rssi_list),self.current_wifi_obs))/len(self.current_wifi_obs)
				
				#print "averaged_ap_num", averaged_ap_num, "averaged_max_rssi", averaged_max_rssi
				#if averaged_ap_num >= 10 and averaged_max_rssi > -80:
				#	self.might_be_driving = 0	
				#else:
				#	self.might_be_driving = 1
				print wifi_matrix_mean
				if wifi_matrix_mean > 115:
					self.must_be_static = 1
				else:
					self.must_be_static = 0

				if wifi_matrix_mean < 70 and len(self.current_wifi_obs) > 0:
					self.must_be_driving = 1
				else:
					self.must_be_driving = 0


		if (isinstance(sensor_reading,Accel)) :
			''' compute accel magnitude and keep track of windows '''
			accel_mag=sqrt(sensor_reading.accel_x**2+sensor_reading.accel_y**2+sensor_reading.accel_z**2)
		        self.current_window=filter(lambda x : x[0] >=  current_time - self.WINDOW_IN_MILLI_SECONDS,self.current_window)
		        self.current_window+=[(current_time,accel_mag)]
			start_time = self.current_window[0][0]

			self.last_print_out=current_time if self.last_print_out == -1 else self.last_print_out
			if (current_time - self.last_print_out) >= self.WINDOW_IN_MILLI_SECONDS/2.0 :
				self.last_print_out = current_time	
				''' variance and mean feature vector components '''
				(mean,variance)=self.mean_and_var(map(lambda x : x[1],self.current_window));
				sigma=sqrt(variance)
				#print "Mean, sigma ",mean,sigma

				''' Peak frequency, compute DFT first on accel magnitudes '''
				current_dft=rfft(map(lambda x : x[1] , self.current_window))
				peak_freq=0 # TODO Find a better way of doing this.
				if (len(current_dft) > 1) :
					''' ignore DC component '''
					peak_freq_index=numpy.abs(current_dft[1:]).argmax() + 1;
					''' sampling_frequency '''
					N=float(len(self.current_window))
					sampling_freq=N/(self.current_window[-1][0]-self.current_window[0][0])
					peak_freq=((peak_freq_index)/(N* 1.0)) * sampling_freq
					nyquist_freq=sampling_freq/2.0;
					assert ( peak_freq <= nyquist_freq );
					#print "Peak_freq ",peak_freq," Hz"

				''' Strength variation '''
				summits=[]
				valleys=[]
				sigma_summit=0
				sigma_valley=0
				for i in range(1,len(self.current_window)-1) :
					if ( (self.current_window[i][1] >= self.current_window[i+1][1]) and (self.current_window[i][1] >= self.current_window[i-1][1]) ) :
						summits+=[self.current_window[i]]
					if ( (self.current_window[i][1] <= self.current_window[i+1][1]) and (self.current_window[i][1] <= self.current_window[i-1][1]) ) :
						valleys+=[self.current_window[i]]
				if ( len(summits) != 0 ) :

					if self.mean_and_var(map(lambda x: x[1], summits))[1] > 0:
						sigma_summit=sqrt(self.mean_and_var(map(lambda x : x[1],summits))[1]);
				if ( len(valleys) != 0 ) :
					if self.mean_and_var(map(lambda x: x[1], valleys))[1] > 0:
						sigma_valley=sqrt(self.mean_and_var(map(lambda x : x[1],valleys))[1]);
				#print "Strength variation ", sigma_valley+sigma_summit
				#posterior_dist=self.predict_label(mean,sigma,peak_freq,sigma_valley+sigma_summit)
				posterior_dist=self.predict_label_with_wifi_hint(mean,sigma,peak_freq,sigma_valley+sigma_summit, self.must_be_driving, self.must_be_static)
				print "Yuhan Posterior", posterior_dist
				print "gnd_truth", sensor_reading.gnd_truth
				#self.classifier_output.append((current_time,posterior_dist))
				# Arbitrary values for unit test :
				self.simple_energy_adapt(current_time, self.power_accel, self.callback_list, posterior_dist.pmf)
				self.last_energy_update=current_time
					
				#self.classifier_output.append((current_time,posterior_dist))

				## EWMA
				current_prediction = posterior_dist.mode()
				ALPHA = 0.15
				Yt = [0]*5
				Yt[current_prediction] = 1
				for i in range(5):
					self.ewma_window[i] = ALPHA * Yt[i] + (1-ALPHA) * self.ewma_window[i]
					
				print "ewma", self.ewma_window
				maxIndex = self.ewma_window.index(max(self.ewma_window))
				pmf = [0]*5
				pmf[maxIndex] = 1
				self.classifier_output.append((current_time,Distribution(5, pmf)))

	def simple_energy_adapt(self, current_time, power_accel, callback_list, posterior_pmf):
			''' Vary sampling rate if confidence > 0.2'''
			self.energy_consumed += (current_time-self.last_energy_update) * power_accel[self.current_sampling_interval]
			print "Current sampling interval is ",self.current_sampling_interval
			
			#ramp up if required
			#do_i_ramp_up=reduce(lambda acc, update : acc or ((posterior_pmf[update] >= 0.2) and (posterior_pmf[update]<=0.8)), callback_list ,False); 
			do_i_ramp_up=reduce(lambda acc, update : acc or ((posterior_pmf[update] >= 0.2)), callback_list ,False); 
			if (do_i_ramp_up):
				candidate_interval = filter(lambda x : x < self.current_sampling_interval,power_accel)
				if len(candidate_interval) > 0:
					self.current_sampling_interval = max(candidate_interval)
					self.sim_phone.change_accel_interval(self.current_sampling_interval)
				return
			else:
				candidate_interval = filter(lambda x : x > self.current_sampling_interval,power_accel)
				if len(candidate_interval) > 0:
					self.current_sampling_interval = min(candidate_interval)
					self.sim_phone.change_accel_interval(self.current_sampling_interval)
				return
