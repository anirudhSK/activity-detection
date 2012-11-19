#! /usr/bin/python 
''' Framework to evaluate classifiers on user generated traces.
    Use traces of arbitrary length to test the classifier.
'''
import sys
from classify import *
from phone import *
from stats import *
if __name__ == "__main__" :
	if ( len(sys.argv) < 8 ) :
		print "Usage: ",sys.argv[0]," accel_trace wifi_trace gps_trace gsm_trace nwk_loc_trace power_model classifier_model "
		exit(5)
	accel_trace=sys.argv[1]
	wifi_trace=sys.argv[2]
	gps_trace=sys.argv[3]
	gsm_trace=sys.argv[4]
	nwk_loc_trace=sys.argv[5]
	power_model=sys.argv[6]
	classifier_model=sys.argv[7]
	''' Initialize phone object '''
	sim_phone=Phone(accel_trace,wifi_trace,gps_trace,gsm_trace,nwk_loc_trace)
	''' Initialize classifier object '''
	classifier=Classify(sim_phone,classifier_model)
	''' run classifier on phone '''
	sampling_rate_vector=sim_phone.run_classifier(classifier)
	''' print statistics '''
	statistics=Stats(sim_phone.gnd_truth,classifier.classifier_output,sampling_rate_vector,power_model)
	print statistics.match(match_type='hard')
