#! /usr/bin/python
''' Continuous time Markov Chain to simulate state transitions '''
from random import *
from math import *
class MarkovChain(object) :
	states=[] 		# list of states id'ed by name
	def __init__ (self,num) :
		seed(num)	
		self.states=['static','walking','running','driving']
	def simulate(self,duration) :
		time=0;
		''' initially, pick state with a uniform prior '''
		state = min(int(random() * 4),4) # sample between 0 and 4 uniformly
		sampled_dtmc=[]
		while ( time < duration ) :
			''' generate next state using all possible jumps from here '''
			sampled_dtmc+=[(time,state)]
			transition_time=self.sample_exp(1/900000.0); # 1 per 10 min or 1 /600000 sec -1
			# pick next_state at random
			next_state=min(int(random() * 3),3) # sample between 0 and 3 uniformly
			target_state=(state+1+next_state)%4# cyclic addition
			assert(target_state!=state)
			state=target_state
			time+=transition_time
		return sampled_dtmc	
	def sample_exp(self,rate) :
		return -log(random())/rate;	
