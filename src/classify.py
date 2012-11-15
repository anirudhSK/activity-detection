#! /usr/bin/python
# classify based on traces
class Classify :
	def __init__(self,sim_phone) :
		self.sim_phone=sim_phone
	def callback(self,sensor_reading,current_time,reading_type) :
		a=5; # TODO
