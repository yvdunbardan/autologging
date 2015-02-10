import time, threading, sys, subprocess

interval_in_minutes = sys.argv[1]
recording_duration = 60 	# Capture Traffic for 60 seconds (1 minutes)

def StartUDPCapture( udp_filename ):
    print "Starting UDP Capture into", udp_filename
    print (time.ctime())
	
    # start the process and return a handle to the process
    return subprocess.Popen([ './tcpdump', '-i', 'eth0', 'udp','-w', udp_filename ],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	    
def StopUDPCapture( tcpdump_process ):
    print "Stopping UDP Capture"
    print (time.ctime())
    tcpdump_process.terminate()

def CaptureUDPTraffic():
    udp_filename = time.strftime("%y-%b-%d_%H-%M" ) + ".pcap"
    tcpdump_process = StartUDPCapture( udp_filename )
    time.sleep(recording_duration)
    StopUDPCapture( tcpdump_process )
    	
print (time.ctime())

while(1):
    if ((int(time.time())-(recording_duration/2)) % (int(interval_in_minutes)*60) == 0):
        CaptureUDPTraffic()
