import time, threading, sys, subprocess, os

# ------------------------------------------------------------------
# Print the usage to the console
# ------------------------------------------------------------------
def PrintUsage():
    print "Usage: udp_capture.py [CaptureInterval] [CaptureDuration]"
    print " where [CaptureInterval] is the intervals where UDP traffic is recorded."
    print " and   [CaptureDuration] is the length of time (in seconds) that the"
    print " traffic is recorded."

# ------------------------------------------------------------------
# Start capturing udp traffic
# ------------------------------------------------------------------
def StartUDPCapture( udp_filename ):
    print "Starting UDP Capture into", udp_filename
    print (time.ctime())
	
    # start the process and return a handle to the process
    return subprocess.Popen([ './tcpdump', '-i', 'eth0', 'udp','-w', udp_filename ],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# ------------------------------------------------------------------
# Stop Capturing traffic
# ------------------------------------------------------------------
def StopUDPCapture( tcpdump_process ):
    print "Stopping UDP Capture"
    print (time.ctime())
    tcpdump_process.terminate()

# ------------------------------------------------------------------
# Start and Stop UDP Capture
# ------------------------------------------------------------------
def CaptureUDPTraffic(recording_duration):
    udp_filename = time.strftime("%y-%b-%d_%H-%M" ) + ".pcap"
    tcpdump_process = StartUDPCapture( os.path.join( "/mnt/hd1/Logs", udp_filename ))
    time.sleep( recording_duration )
    StopUDPCapture( tcpdump_process )

# ------------------------------------------------------------------
# Main
#
# Get the command line arguments
# Enter an infinite loop, triggering to CaptureUDPTraffic at interval specified by the user
# ------------------------------------------------------------------
print (time.ctime())

try:
    # Get command line arguments
    interval_in_minutes = int(sys.argv[1])      # Interval to start capturing in minutes
    recording_duration = int(sys.argv[2]) 	# Capture Traffic for x seconds

    # Loop
    while(1):
        if ( (int( time.time() ) + ( recording_duration/2 )) % (interval_in_minutes*60) == 0):
            CaptureUDPTraffic(recording_duration)
except:
    PrintUsage()
    sys.exit(1)
    
