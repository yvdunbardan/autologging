#!/bin/sh
# *
# * YVStart_humax_hdd.sh
# *
# *  Created on: 30 Aug 2012
# *      Author: Ash
# *  Modified on: 6 Feb 2014
# *      After speaking with DevArch, starting of YV Services is not needed, and actually is already done so.
# *      Author: Dan Dunbar

sleep 5

echo
mkdir -p /mnt/hd1/Logs 2>/dev/null 1>/dev/null

echo "Deleting old dbus log files !!!"
find /mnt/hd1/Logs/ -mtime +5 -exec rm {} \; 2>/dev/null

NOW=`date +"%F_%H_%M_%S"`
DVRLOGFILE=/mnt/hd1/Logs/stb_dvr_profile_log_${NOW}.txt
LOGFILE=/mnt/hd1/Logs/stb_dbus_log_${NOW}.txt
MEMLOGFILE=/mnt/hd1/Logs/stb_vmstat_log_${NOW}.txt

vmstat -S K -n 1800 > ${MEMLOGFILE} &
dbus-monitor >> ${LOGFILE} &

sleep 10
python -u /mnt/hd1/DVRProfiler.py >> ${DVRLOGFILE} &
chmod 777 ${DVRLOGFILE}
chmod 777 ${LOGFILE}

# Start TCP Dump logging
/mnt/hd1/tcpdump ip proto 2 -w ./Logs/igmp-$NOW.pcap &
python -u /mnt/hd1/udp_capture.py 900 20 &


