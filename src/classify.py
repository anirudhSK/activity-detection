#! /usr/bin/python
from sensors import *
from math import *
from numpy.fft import *
import numpy
from normal import *
from distributions import *
# classify based on traces
class Classify(object) :
	''' Windowing primitives '''
	last_print_out=-1
	WINDOW_IN_MILLI_SECONDS=5000
	SHIFT_TIME_MILLI_SECONDS=1000
	current_window=[]

	''' parameters of distributions used for Naive Bayes prediction '''
	mean_fv_dist=[0]*5
	sigma_fv_dist=[0]*5
	peak_freq_fv_dist=[0]*5
	strength_var_fv_dist=[0]*5

	def __init__(self,sim_phone,classifier_model) :
		self.sim_phone=sim_phone
		self.classifier_output=[]

		''' set initial sampling intervals in milliseconds '''
		sim_phone.change_accel_interval(10)
		sim_phone.change_wifi_interval(1000)
		sim_phone.change_gps_interval(1000)
		sim_phone.change_gsm_interval(1000)
		sim_phone.change_nwk_loc_interval(1000)

		execfile(classifier_model)
		
	def mean_and_var(self,value_list) :
		if (value_list==[]) :
			return (None,None)
		meanSq=reduce(lambda acc,update : acc + update**2,value_list,0.0)/len(value_list)
		mean=reduce(lambda acc,update : acc + update,value_list,0.0)/len(value_list)
		return (mean,meanSq-mean*mean)

	def predict_label(self,mean_fv,sigma_fv,peak_freq_fv,strength_var_fv) :
		''' Predict the label given the mean, sigma, peak frequency and strength variation components of the feature vector '''
		likelihood=[0]*5
		for label in range(0,5) :
			likelihood[label] = (self.mean_fv_dist[label].pdf(mean_fv))   * (self.sigma_fv_dist[label].pdf(sigma_fv)) * (self.peak_freq_fv_dist[label].pdf(peak_freq_fv)) * (self.strength_var_fv_dist[label].pdf(strength_var_fv))
		posterior_pmf=[0]*5
		for label in range(0,5) :
			posterior_pmf[label]=likelihood[label]/sum(likelihood)
		return	Distribution(5,posterior_pmf)

	def callback(self,sensor_reading,current_time) :
		''' Interface to simulator :  Leave final result as (timestamp,output_distribution) pairs in classifier_output '''
		if (isinstance(sensor_reading,Accel)) :
			print "\n"
			''' compute accel magnitude and keep track of windows '''
			accel_mag=sqrt(sensor_reading.accel_x**2+sensor_reading.accel_y**2+sensor_reading.accel_z**2)
		        self.current_window=filter(lambda x : x[0] >=  current_time - self.WINDOW_IN_MILLI_SECONDS,self.current_window)
		        self.current_window+=[(current_time,accel_mag)]
			if (current_time - self.last_print_out >= self.SHIFT_TIME_MILLI_SECONDS) :
				''' variance and mean feature vector components '''
				(mean,variance)=self.mean_and_var(map(lambda x : x[1],self.current_window));
				sigma=sqrt(variance)
				print "Mean, sigma ",mean,sigma

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
					print "Peak_freq ",peak_freq," Hz"

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
					sigma_summit=sqrt(self.mean_and_var(map(lambda x : x[1],summits))[1]);
				if ( len(valleys) != 0 ) :
					sigma_valley=sqrt(self.mean_and_var(map(lambda x : x[1],valleys))[1]);
				print "Strength variation ", sigma_valley+sigma_summit
				self.classifier_output.append((current_time,self.predict_label(mean,sigma,peak_freq,sigma_valley+sigma_summit)))
