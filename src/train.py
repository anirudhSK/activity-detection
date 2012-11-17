#! /usr/bin/python
# train based on traces
from sensors import *
class Train(object) :
	def __init__(self,sim_phone) :
		self.sim_phone=sim_phone
	def callback(self,sensor_reading,current_time,gnd_truth) :
		a=5; # TODO
		print "Training !! "
		print type(sensor_reading)
		''' Print out any training relevant information to a file '''
