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
	def callback(self,sensor_reading,current_time,gnd_truth) :
		if (isinstance(sensor_reading,Accel)) :
			''' compute accel magnitude and keep track of windows '''
			accel_mag=sqrt(sensor_reading.accel_x**2+sensor_reading.accel_y**2+sensor_reading.accel_z**2)
		        self.current_window=filter(lambda x : x[0] >=  current_time - self.WINDOW_IN_SECONDS,self.current_window)
		        self.current_window+=[(current_time,accel_mag)]
			if (current_time - self.last_print_out >= self.SHIFT_TIME) :
				''' variance and mean feature vector components '''
				meanSq=reduce(lambda acc,update : acc + update[1]*update[1],self.current_window,0)/len(self.current_window)
				mean=reduce(lambda acc,update : acc + update[1],self.current_window,0)/len(self.current_window)
				variance=meanSq-mean*mean;
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
		''' Print out any training relevant information to a file '''
