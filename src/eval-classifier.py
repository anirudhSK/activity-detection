#! /usr/bin/python 
''' Framework to evaluate classifiers on user generated traces.
    Use traces of arbitrary length to test the classifier.
'''
import sys
from classify import *
from phone import *
from stats import *
if __name__ == "__main__" :
	if ( len(sys.argv) < 9 ) :
		print "Usage: ",sys.argv[0]," accel_trace wifi_trace gps_trace gsm_trace nwk_loc_trace power_model classifier_model sampling_interval_ms"
		exit(5)
	accel_trace=sys.argv[1]
	wifi_trace=sys.argv[2]
	gps_trace=sys.argv[3]
	gsm_trace=sys.argv[4]
	nwk_loc_trace=sys.argv[5]
	power_model=sys.argv[6]
	classifier_model=sys.argv[7]
	sampling_interval = float(sys.argv[8])
	''' Initialize phone object '''
	sim_phone=Phone(accel_trace,wifi_trace,gps_trace,gsm_trace,nwk_loc_trace)
	''' Initialize classifier object '''
	classifier=Classify(sim_phone,classifier_model,sampling_interval)
	''' run classifier on phone '''
	sampling_rate_vector=sim_phone.run_classifier(classifier)
	''' print statistics '''
	statistics=Stats(sim_phone.gnd_truth,classifier.classifier_output,sampling_rate_vector,power_model)
	print>>sys.stderr,"Hard match ",statistics.match(match_type='hard')
	print>>sys.stderr,"Soft match ",statistics.match(match_type='soft')
	print>>sys.stderr,"Detection latency : \n -----------"
	statistics.latency_stats()
	print "Graph data :"
	fh=open("classifier.plot","w");
	for output in classifier.classifier_output :
		fh.write(str(output[0])+"\t"+str(output[1].mode())+"\n");
	fh=open("gnd.plot","w");
	for output in sim_phone.gnd_truth :
		fh.write(str(output[0])+"\t"+str(output[1].mode())+"\n");
