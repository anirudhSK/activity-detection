#! /usr/bin/python
from markov import *
from trace import *
''' Program to stitch traces together into a larger trace '''
import sys
from os import *
from os.path import *
if ( len(sys.argv) < 5) :
	print "Usage : python ",sys.argv[0]," duration_in_ms indoor_trace_folder outdoor_trace_folder random_seed "
	exit(5)
else :
	duration=int(sys.argv[1]);
	indoor_trace_folder=sys.argv[2]
	outdoor_trace_folder=sys.argv[3]

	''' Extract traces from folders '''	
	indoor_traces =  map(lambda x : Trace (join(indoor_trace_folder,x))  ,
			filter(lambda x : isfile(join(indoor_trace_folder,x)) ,listdir(indoor_trace_folder)))
	outdoor_traces=  map(lambda x : Trace (join(outdoor_trace_folder,x)) ,
			filter(lambda x : isfile(join(outdoor_trace_folder,x)),listdir(outdoor_trace_folder)))

	''' Indices to keep track of which trace file to write next '''
	indoor_index =0
	outdoor_index=0

	random_seed=int(sys.argv[4]);
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
			indoor_traces[indoor_index].rewrite_trace_file(start,end);
			print "Using indoor_index ",indoor_index
			indoor_index=(indoor_index+1)%len(indoor_traces)
		elif ( current_activity == 1 ) 	:
			outdoor_traces[outdoor_index].rewrite_trace_file(start,end);
			print "Using outdoor_index ",outdoor_index
			outdoor_index=(outdoor_index+1)%len(outdoor_traces)
