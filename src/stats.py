#! /usr/bin/python
# generate classification stats
class Stats :
	gnd_truth=[]		# list of time, gnd_truth pairs
	classifier_output=[]	# list of time, classifier output pairs
	class Interval :	# Represents a closed Interval on the time axis with a gnd truth
		start=0
		end=0
		gnd_truth=-1
		def get_length(self) :
			return end-start
		def __init__ (self,start,end,gnd_truth) :
			self.start=start
			self.end=end
			self.gnd_truth=gnd_truth
		def get_overlap(self,interval) :
			if   ((interval.start >= self.end) or (interval.end <= self.start)) :   # outside
				return 0
			elif ((interval.start >= self.start) and (interval.end <= self.end) ) : # engulfed
				return interval.get_length()
			elif ((interval.start <= self.start) and (interval.end >= self.end) ) : # engulfing
				return self.get_length()
			elif ((interval.start <= self.start) and (interval.end <= self.end) ) : # left overlap
				return interval.end-self.start
			elif ((interval.start >= self.start) and (interval.end >= self.end) ) : # right overlap
				return self.end-interval.start
				
	def __init__ (self,gnd_truth,classifier_output) :
		self.gnd_truth=gnd_truth
		self.classifier_output=classifier_output
	def hard_match(self):	# compute hard path metric between the two lists
		# compute intervals for both lists
		gnd_truth_list=interval_list(gnd_truth)
		classifier_output_list=interval_list(classifier_output)
		correct_match_time=0
		incorrect_match_time=0
		for gnd_truth_interval in range (0,len(gnd_truth_list)) :
			classifier_filtered=filter(lambda x : not (x.end >= gnd_truth_interval.end) or (x.start <= gnd_truth_interval.start), classifier_output_list)
			for output_interval in classifier_filtered :
				if (output_interval==gnd_truth_interval.gnd_truth) :
					correct_match_time+=self.overlap(output_interval,gnd_truth_interval)
				else :
					incorrect_match_time+=self.overlap(output_interval,gnd_truth_interval)
		return float(correct_match_time) / ( correct_match_time + incorrect_match_time )
	def soft_match(self):	# compute soft path metric between the two lists
		return 0 	# TODO
	def latency_stats(self):# compute latency of detection
		return [] 	# TODO
	def interval_list(self,time_series) :
		''' Compute a range-list that says time 1 to time 2 activity 1, and so on '''
		last_gnd_truth=time_series[0][1]
		last_time_stamp=time_series[0][1]
		interval_list=[]
		for pair in time_series :
			time_stamp=pair[0]
			gnd_truth=pair[1]
			if ( gnd_truth != last_gnd_truth ) :
				interval_list.append(Interval(last_gnd_truth,last_time_stamp,time_stamp))
				last_gnd_truth = gnd_truth
				last_time_stamp=time_stamp
		interval_list.append(Interval(last_gnd_truth,last_time_stamp,time_series[len(time_series)-1][0]))	# termination 
		return interval_list
