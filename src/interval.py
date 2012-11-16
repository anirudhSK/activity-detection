#! /usr/bin/python
# represent an interval
class Interval :	# Represents a closed Interval on the time axis with a gnd truth
	start=0
	end=0
	gnd_truth=-1
	def get_length(self) :
		return self.end-self.start
	def __init__ (self,start,end,gnd_truth) :
		self.start=start
		self.end=end
		self.gnd_truth=gnd_truth
	def __str__(self) :
		return "Interval: start "+str(self.start)+", end "+str(self.end)+", gnd "+str(self.gnd_truth)
	def __repr__(self) :
		return str(self)
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
