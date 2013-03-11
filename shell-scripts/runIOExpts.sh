#! /bin/bash
# run IO Detector experiments
i=0
# train Galaxy Nexus Model
cd ~/cita/activity-detection/src
python train-classifier.py ~/cita/io-detector/IO-Data/io-data-Dec3/Accel-dummy ~/cita/io-detector/IO-Data/io-data-Dec3/Wifi-Lenin ~/cita/io-detector/IO-Data/io-data-Dec3/GPS-dummy ~/cita/io-detector/IO-Data/io-data-Dec3/GSM-Lenin ~/cita/io-detector/IO-Data/io-data-Dec3/NwkLoc-dummy ../hardware-model/galaxy/power.py 2> galaxy.model
###
#### Stitch traces once and for all
###while [ $i -lt 10 ] ; do
###  cd ~/cita/activity-detection/utils
###  echo "Stitching seed $i"
###  ./split-and-stitch.sh ~/cita/io-detector/IO-Data/io-data-Dec6/GalaxyNexus/ 10800000 $i	> /dev/null
###  cp ../utils/stitched-Accel.out ../utils/stitched-Accel-$i.out
###  cp ../utils/stitched-Wifi.out ../utils/stitched-Wifi-$i.out
###  cp ../utils/stitched-GPS.out ../utils/stitched-GPS-$i.out
###  cp ../utils/stitched-GSM.out ../utils/stitched-GSM-$i.out
###  cp ../utils/stitched-GeoLoc.out ../utils/stitched-GeoLoc-$i.out
###  i=`expr $i '+' 1`
###done
###
# run 6 latencies
latency=10000
while [ $latency -lt 70000 ]; do
  # clear old results
  rm /tmp/io-results.txt
  # run 10 iterations
  i=0
  while [ $i -lt 10 ] ; do
    echo " Running seed $i"
    cd ~/cita/activity-detection/src
    python eval-classifier.py ../utils/stitched-Accel-$i.out ../utils/stitched-Wifi-$i.out ../utils/stitched-GPS-$i.out ../utils/stitched-GSM-$i.out ../utils/stitched-GeoLoc-$i.out ../hardware-model/galaxy/power.py galaxy.model $latency > /dev/null 2>> /tmp/io-results.txt
    i=`expr $i '+' 1`
  done
  # Run print-stats.py on the results
  cd ~/cita/activity-detection/utils/
  echo "Latency :"$latency
  cat /tmp/io-results.txt | sed 's/\[1, 2\]/\[1,2\]/g' |  python print_stats.py
  latency=`expr $latency '+' 10000`
done
