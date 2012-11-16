#! /usr/bin/python 
''' Framework to evaluate classifiers on user generated traces.
    Allows you to create traces of arbitrary length to test the classifier.
'''
import sys
from classify import *
from phone import *
from stats import *
if __name__ == "__main__" :
	if ( len(sys.argv) < 6 ) :
		print "Usage: ",sys.argv[0]," accel-trace wifi-trace gps-trace gsm-trace nwk-loc-trace "
		exit(5)
	accel_trace=sys.argv[1]
	wifi_trace=sys.argv[2]
	gps_trace=sys.argv[3]
	gsm_trace=sys.argv[4]
	nwk_loc_trace=sys.argv[5]	
	''' Initialize phone object '''
	sim_phone=Phone(accel_trace,wifi_trace,gps_trace,gsm_trace,nwk_loc_trace)
	''' Initialize classifier object '''
	classifier=Classify(sim_phone)
	''' run classifier on phone '''
	sim_phone.run_classifier(classifier)
	''' print statistics '''
	statistics=Stats([],[])	
