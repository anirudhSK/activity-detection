#! /usr/bin/python
# train based on traces
class Train :
	def __init__(self,sim_phone) :
		self.sim_phone=sim_phone
	def callback(self,sensor_reading,current_time,reading_type,gnd_truth) :
		a=5; # TODO
		print "Training !! "
		''' Print out any training relevant information to a file '''
