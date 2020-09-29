#!/bin/bash

DATE=`date +%Y-%m-%d`
echo "$DATE"
echo "Activate VirtualEnv"
source /home/pi/Documents/flight_monitor/venv/bin/activate
echo "Call Script"
python /home/pi/Documents/flight_monitor/crawl_sas.py
for i in {1..80}; do echo -n '='; done
echo ""
