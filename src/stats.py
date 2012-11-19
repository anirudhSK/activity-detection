#! /usr/bin/python
# generate classification stats
from interval import *
from distributions import *
class Stats(object) :
	gnd_truth=[]		# list of time, gnd_truth pairs
	classifier_output=[]	# list of time, classifier output pairs
	sampling_intervals=()# 5 tuple of lists each representing one sensor's rate as a fn of time
	
	''' power stats for each phone '''
	power_accel=dict()
	power_wifi=dict()
	power_gps=dict()
	power_gsm=dict()
	power_nwk_loc=dict()
	def __init__ (self,gnd_truth,classifier_output,sensor_sampling_intervals,power_model) :
		self.gnd_truth=gnd_truth
		self.classifier_output=classifier_output
		self.sampling_intervals=sensor_sampling_intervals
		execfile(power_model)
	def match(self,match_type='hard'):	# compute hard or soft path metric between the two lists
		# compute intervals for both lists
		gnd_truth_list=self.interval_list(self.gnd_truth)
		classifier_output_list=self.interval_list(self.classifier_output)
		correct_match_time=0
		total_time=0
		for gnd_truth_interval in gnd_truth_list :
			classifier_filtered=filter(lambda x : not ((x.start >= gnd_truth_interval.end) or (x.end <= gnd_truth_interval.start)), classifier_output_list)
			for output_interval in classifier_filtered :
				overlap=output_interval.get_overlap(gnd_truth_interval)
				assert(overlap>=0)
				if ( match_type == 'hard' ) :
					if (output_interval.distribution.mode()==gnd_truth_interval.distribution.mode()) :
						correct_match_time+=overlap
				elif(match_type == 'soft' ) :
						correct_match_time+=overlap*(output_interval.distribution*gnd_truth_interval.distribution)
				total_time+=overlap
		return float(correct_match_time) / ( total_time )
	def latency_stats(self):# compute latency of detection
		return [] 	# TODO
	def energy_stats(self): # compute energy cost of detection over the entire trace
		accel_sampling_intervals=sampling_intervals[0]
		wifi_sampling_intervals=sampling_intervals[1]
		gps_sampling_intervals=sampling_intervals[2]
		gsm_sampling_intervals=sampling_intervals[3]
		nwk_loc_sampling_intervals=sampling_intervals[4]
		energy=0
		for i in range(0,len(accel_sampling_intervals)-1) :
			energy+=self.power_accel[accel_sampling_intervals[i][1]]*(accel_sampling_intervals[i+1][0]-accel_sampling_intervals[i][0])
		for i in range(0,len(wifi_sampling_intervals)-1) :
			energy+=self.power_wifi[wifi_sampling_intervals[i][1]]*(wifi_sampling_intervals[i+1][0]-wifi_sampling_intervals[i][0])
		for i in range(0,len(gps_sampling_intervals)-1) :
			energy+=self.power_gps[gps_sampling_intervals[i][1]]*(gps_sampling_intervals[i+1][0]-gps_sampling_intervals[i][0])
		for i in range(0,len(gsm_sampling_intervals)-1) :
			energy+=self.power_gsm[gsm_sampling_intervals[i][1]]*(gsm_sampling_intervals[i+1][0]-gsm_sampling_intervals[i][0])
		for i in range(0,len(accel_sampling_intervals)-1) :
			energy+=self.power_nwk_loc[nwk_loc_sampling_intervals[i][1]]*(nwk_loc_sampling_intervals[i+1][0]-nwk_loc_sampling_intervals[i][0])
		return energy	
	def interval_list(self,time_series) :
		''' Compute a range-list that says time 1 to time 2 distribution 1, and so on '''
		last_time_stamp=time_series[0][0]
		last_distribution=time_series[0][1]
		interval_list=[]
		for pair in time_series :
			time_stamp=pair[0]
			current_distribution=pair[1]
			if ( current_distribution != last_distribution ) :
				interval_list.append(Interval(start=last_time_stamp,end=time_stamp,distribution=last_distribution))
				last_distribution = current_distribution
				last_time_stamp=time_stamp
		interval_list.append(Interval(start=last_time_stamp,end=time_series[len(time_series)-1][0],distribution=last_distribution))	# termination
		return interval_list
