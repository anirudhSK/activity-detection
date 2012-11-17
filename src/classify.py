#! /usr/bin/python
# classify based on traces
class Classify(object) :
	def __init__(self,sim_phone) :
		self.sim_phone=sim_phone
		self.classifier_output=[]
	def callback(self,sensor_reading,current_time) :
		a=5; # TODO
		''' Interface to simulator :  Leave final result as (timestamp,output_state) pairs in classifier_output '''
