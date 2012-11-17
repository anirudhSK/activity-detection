#! /usr/bin/python
# train based on traces
from sensors import *
from math import *
from numpy.fft import *
import numpy
class Train(object) :
	last_print_out=-1
	WINDOW_IN_SECONDS=5
	SHIFT_TIME=1
	current_window=[]
	def __init__(self,sim_phone) :
		self.sim_phone=sim_phone
	def mean_and_var(self,value_list) :
		meanSq=reduce(lambda acc,update : acc + update**2,value_list,0.0)/len(value_list)
		mean=reduce(lambda acc,update : acc + update,value_list,0.0)/len(value_list)
		return (mean,meanSq-mean*mean)

	def callback(self,sensor_reading,current_time,gnd_truth) :
		if (isinstance(sensor_reading,Accel)) :
			print "\n"
			''' compute accel magnitude and keep track of windows '''
			accel_mag=sqrt(sensor_reading.accel_x**2+sensor_reading.accel_y**2+sensor_reading.accel_z**2)
		        self.current_window=filter(lambda x : x[0] >=  current_time - self.WINDOW_IN_SECONDS,self.current_window)
		        self.current_window+=[(current_time,accel_mag)]
			if (current_time - self.last_print_out >= self.SHIFT_TIME) :
				''' variance and mean feature vector components '''
				(mean,variance)=self.mean_and_var(map(lambda x : x[1],self.current_window));
				print "Mean, variance ",mean,variance

				''' Peak frequency, compute DFT first on accel magnitudes '''
				current_dft=rfft(map(lambda x : x[1] , self.current_window))
				if (len(current_dft) > 1) :
					''' ignore DC component '''
					peak_freq_index=current_dft[1:].argmax() + 1;
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
		''' Print out any training relevant information to a file '''
