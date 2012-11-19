#! /usr/bin/python
from markov import *
from trace import *
''' Program to stitch traces together into a larger trace '''
import sys
if ( len(sys.argv) < 8) :
	print "Usage : python markov-chain.py duration_in_ms static_trace walking_trace running_trace biking_trace driving_trace random_seed "
	exit(5)
else :
	duration=int(sys.argv[1]);
	static_trace =Trace(sys.argv[2])
	walking_trace=Trace(sys.argv[3])
	running_trace=Trace(sys.argv[4])
	biking_trace =Trace(sys.argv[5])
	driving_trace=Trace(sys.argv[6])
	random_seed=int(sys.argv[7]);
	m=MarkovChain(random_seed)
	sampled_dtmc=m.simulate(duration);
	for i in range(0,len(sampled_dtmc)) :
		current=sampled_dtmc[i]
		if ( i < len(sampled_dtmc) -1 ) :
			next_change=sampled_dtmc[i+1]
			end=next_change[0]
		else :
			end=duration
		start=current[0]
		current_activity=current[1]
		if ( current_activity == 0 ) 	:
			static_trace.rewrite_trace_file(start,end);
		elif ( current_activity == 1 ) 	:
			walking_trace.rewrite_trace_file(start,end);
		elif ( current_activity == 2 ) 	:
			running_trace.rewrite_trace_file(start,end);
		elif ( current_activity == 3 ) 	:
			biking_trace.rewrite_trace_file(start,end);
		elif ( current_activity == 4 ) 	:
			driving_trace.rewrite_trace_file(start,end);
