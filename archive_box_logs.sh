# ------------------------------------------------------------
# Script that collects, archives and clears out old log files.
# It also starts or creates a new set of logs
# ------------------------------------------------------------
#! /bin/bash

# Kill dbus-monitor, tcpdump and vmstat processes
killall dbus-monitor tcpdump vmstat 2> /dev/null

# kill all DVRProfiler processes
ps aux | grep DVRProfiler | awk '{print $2}' | xargs kill 2> /dev/null

# Setup the tmp directory and copy the most recent dbus, stat and dvrprofiler logs
cd /mnt/hd1/Logs; mkdir -p archive; rm -rf ./tmp; mkdir -p tmp; cp *.* ./tmp

# Archive the zinc logs
cd /mnt/hd1/Logs; tar -cvzf ./tmp/zinc-logs-$STB-`date +"%Y_%m_%d_%H_%M"`.tgz $(find /opt/zinc/var/ -name "*.log") 2> /dev/null

# Move them to the tmp directory, and archive all the files in there
cd tmp; tar -czf ../archive/all-logs-$STB-`date +"%Y_%m_%d_%H_%M"`.tgz ./*

# Clear out the logs directory, and restore the most recent logs from tmp, and remove tmp
cd /mnt/hd1/Logs; rm -rf tmp;  rm *.*; cd /mnt/hd1;
./YVStart.sh &
./capture_traffic.py 1800 60 25 &

