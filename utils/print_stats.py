#! /usr/bin/python
import numpy
import sys
file_handle=sys.stdin
lines=file_handle.readlines();
i=0
energy_stats=dict()
accuracy_stats=dict()
while i < len(lines) :
	records=lines[i].split()
	if (len(records)>=1) and (records[0]=="Callbacks") :
		callback=records[2]
		accuracy=lines[i+1].split()[2]
		energy=lines[i+2].split()[2]
		if callback not in energy_stats :
			energy_stats[callback]=[float(energy)]
		else :
			energy_stats[callback]+=[float(energy)]
		if callback not in accuracy_stats :
			accuracy_stats[callback]=[float(accuracy)]
		else :
			accuracy_stats[callback]+=[float(accuracy)]
	i=i+1
for callback in energy_stats :
	if callback in accuracy_stats :
		mean_accuracy=100.0*numpy.mean(accuracy_stats[callback])
		stddev_accuracy=100.0*(numpy.std(accuracy_stats[callback])/numpy.sqrt(len(accuracy_stats[callback])-1))
                mean_energy=numpy.mean(energy_stats[callback])
                stddev_energy=numpy.std(energy_stats[callback])/numpy.sqrt(len(energy_stats[callback])-1)
 		print callback,"\t %2.1f"%mean_accuracy,"%2.1f"%(1.96*stddev_accuracy),"%.0f "%mean_energy,"%.0f "%(1.96*stddev_energy)
