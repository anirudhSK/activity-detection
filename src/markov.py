#! /usr/bin/python
''' Continuous time Markov Chain to simulate state transitions '''
from random import *
from math import *
class MarkovChain(object) :
	states=[] 		# list of states id'ed by name
	transition_rates=[] 	# list of lists with transition rates per second
	def __init__ (self,num) :
		seed(num)	
		self.states=['static','walking','running','biking','driving']
		for i in range(0,len(self.states)) :
			self.transition_rates.append([])
			for j in range(0,len(self.states)) :
				self.transition_rates[i].append(1/600000.0); # one transition every 600000 ms
	def simulate(self,duration) :
		time=0;
		''' initially, pick state with a uniform prior '''
		state = min(int(random() * 5),5)
		sampled_dtmc=[]
		while ( time < duration ) :
			''' generate next state using all possible jumps from here '''
			sampled_dtmc+=[(time,state)]
			min_time=-1
			for j in range(0,len(self.states)):
				transition_time=self.sample_exp(self.transition_rates[state][j])
				if (min_time == -1 ) :
					min_time=transition_time
					target_state=j
				elif (transition_time < min_time) :
					min_time=transition_time
					target_state=j		
			state=target_state
			time=time+min_time
		return sampled_dtmc	
	def sample_exp(self,rate) :
		return -log(random())/rate;	
