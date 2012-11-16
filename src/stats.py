#! /usr/bin/python
# generate classification stats
from interval import *
class Stats :
	gnd_truth=[]		# list of time, gnd_truth pairs
	classifier_output=[]	# list of time, classifier output pairs
	sampling_rates=()# 5 tuple of lists each representing one sensor's rate as a fn of time
	def __init__ (self,gnd_truth,classifier_output,sensor_sampling_rates) :
		self.gnd_truth=gnd_truth
		self.classifier_output=classifier_output
		self.sampling_rates=sensor_sampling_rates
	def hard_match(self):	# compute hard path metric between the two lists
		# compute intervals for both lists
		gnd_truth_list=self.interval_list(self.gnd_truth)
		classifier_output_list=self.interval_list(self.classifier_output)
		correct_match_time=0
		incorrect_match_time=0
		print gnd_truth_list
		for gnd_truth_interval in gnd_truth_list :
			classifier_filtered=filter(lambda x : not ((x.start >= gnd_truth_interval.end) or (x.end <= gnd_truth_interval.start)), classifier_output_list)
			for output_interval in classifier_filtered :
				if (output_interval.gnd_truth==gnd_truth_interval.gnd_truth) :
					correct_match_time+=output_interval.get_overlap(gnd_truth_interval)
				else :
					incorrect_match_time+=output_interval.get_overlap(gnd_truth_interval)		
		return float(correct_match_time) / ( correct_match_time + incorrect_match_time )
	def soft_match(self):	# compute soft path metric between the two lists
		return 0 	# TODO
	def latency_stats(self):# compute latency of detection
		return [] 	# TODO
	def energy_stats(self): # compute energy cost of detection over the entire trace
		return -1 	# TODO	
	def interval_list(self,time_series) :
		''' Compute a range-list that says time 1 to time 2 activity 1, and so on '''
		last_time_stamp=time_series[0][0]
		last_gnd_truth=time_series[0][1]
		interval_list=[]
		for pair in time_series :
			time_stamp=pair[0]
			gnd_truth=pair[1]
			if ( gnd_truth != last_gnd_truth ) :
				interval_list.append(Interval(start=last_time_stamp,end=time_stamp,gnd_truth=last_gnd_truth))
				last_gnd_truth = gnd_truth
				last_time_stamp=time_stamp
		interval_list.append(Interval(start=last_time_stamp,end=time_series[len(time_series)-1][0],gnd_truth=last_gnd_truth))	# termination 
		return interval_list
