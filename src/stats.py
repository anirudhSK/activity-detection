#! /usr/bin/python
# generate classification stats
class Stats :
	gnd_truth=[]		# list of time, gnd_truth pairs
	classifier_output=[]	# list of time, classifier outputi pairs
	def __init__ (self,gnd_truth,classifier_output) :
		self.gnd_truth=gnd_truth
		self.classifier_output=classifier_output
	def hard_match(self)	# compute hard path metric between the two lists
		return 0 	# TODO
	def soft_match(self)	# compute soft path metric between the two lists
		return 0 	# TODO
	def latency_stats(self) # compute latency of detection
		return [] 	# TODO
