DATE=`date +%Y-%m-%d`
echo "$DATE"
echo "Activate VirtualEnv"
source ~/Documents/flight_monitor/venv/bin/activate
echo "Call Script"
python crawl_sas.py
for i in {1..80}; do echo -n '='; done
echo ""
