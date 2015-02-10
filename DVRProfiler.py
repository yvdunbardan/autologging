#!/bin/env /opt/zinc/oss/bin/python
'''
Created on 28 Feb 2012

@author: ashutosh
'''


import dbus
import gobject
from dbus.mainloop.glib import DBusGMainLoop
import datetime
import sys
import time
import urllib


RECORDING_BEGUN = 0 
RECORDING_ACQUIRED = 1
RECORDING_PARTIALLY_ACQUIRED = 2
RECORDING_FAILED = 3

RECORDING_LIST_ADDED = 0
RECORDING_LIST_UPDATED = 1
RECORDING_LIST_DELETED = 2

#Event structure
EVENT_TITLE = 4
EVENT_START_TIME = 2
EVENT_DURATION = 3
EVENT_PCRID = 8
EVENT_LOC = 1

BOOKING_LIST_ADDED = 0
BOOKING_LIST_UPDATED=1
BOOKING_LIST_DELETED=2

LibraryContentChangeType_ADDED=0
LibraryContentChangeType_UPDATED=1
LibraryContentChangeType_DELETED=2


evInfo = {'name':None,'start':None,'duration':None,'pcrid':None,'evLoc':None} 
schedRecInfo = {'eventLocator':None,'title':None,'service':None,'duration':None,'startTime':None,'bookingReference':None,'status':None,'pcrid':None}
mrecInfo = {'mediaRecordID':None,'contentIdentifier':None,'mediaLocator':None,'serviceName':None,'title':None,'publishedDuration':None,'duration':None,'watershed':None,'acquisitionDateTime':None,'acquisitionStatus':None,'size':None}
schedRecStatus = {'0':'PENDING','1':'PENDING_IN_SERIES','2':'IN_PROGRESS','3':'IN_PROGRESS_IN_SERIES'}
acqStatus = {'-1':'NOT_BEGUN_YET','0':'BEGUN','1':'ACQUIRED','2':'PARTIALLY_ACQUIRED','3':'FAILED'}
bookingType = {'0':'EVENT','1':'PROGRAM','2':'SERIES'}
bookingInfo = {'bookingReference':None,'title':None,'identifier':None,'booking_type':None}
powerState = {'0':'RESERVED','1':'DEEP_STANDBY','2':'RESERVED','3':'ACTIVE_STANDBY','4':'RESERVED','5':'ON'}


global sched_recs
#shced_recs = [] 


def printDebug(st):
    '''
    wrapper to print with timestamps
    '''
    print '[%s] %s'%(datetime.datetime.now(),st)
#    string='[%s] %s'%(datetime.datetime.now(),st)
#    params=urllib.urlencode({'arg':string})
#    urllib.urlopen("http://192.168.16.208/dvrLog.php?%s"%params)

def getEventInfo(event):
    '''
    function to get the event information
    '''
    ev = eventRepo_iface.getEvent(event)
    evInfo[u'name'] = str(ev[EVENT_TITLE]['eng'])
    evInfo[u'start'] = str(time.ctime(int(ev[EVENT_START_TIME])))
    evInfo[u'duration'] = int(ev[EVENT_DURATION])
    evInfo[u'pcrid'] = str(ev[EVENT_PCRID])
    evInfo[u'evLoc'] = str(ev[EVENT_LOC])
    return evInfo

def getBookingInfo(booking):
    '''
    function to get the booking information
    '''
    booking_info = linearAcq_iface.getBooking(booking)
    bookingInfo[u'bookingReference'] = str(booking_info[0])
    bookingInfo[u'title'] = str(booking_info[1])
    bookingInfo[u'identifier'] = str(booking_info[3])
    bookingInfo[u'booking_type'] = bookingType[str(booking_info[4])]
    return bookingInfo


def getSchedRecInfo(sched_rec):
    '''
    function to get scheduled recording info
    '''
    schedRecInfo['eventLocator'] = str(sched_rec[0])
    schedRecInfo['title'] = str(sched_rec[1])
    schedRecInfo['service'] = str(sched_rec[2])
    schedRecInfo['duration'] = int(sched_rec[3])
    schedRecInfo['startTime'] = str(time.ctime(int(sched_rec[4])))
    schedRecInfo['bookingReference'] = str(sched_rec[5])
    schedRecInfo['status'] = schedRecStatus[str(sched_rec[10])]
    schedRecInfo['pcrid'] = str(sched_rec[6])
    
    return schedRecInfo
    
def getmediaRecInfo(mrec):
    '''
    '''
#    print mrec
    mrecInfo['mediaRecordID'] = str(mrec[0])
    mrecInfo['contentIdentifier'] = str(mrec[1])
    mrecInfo['mediaLocator'] = str(mrec[3])
    mrecInfo['serviceName'] = str(mrec[4])
    mrecInfo['title'] = str(mrec[5])
    mrecInfo['publishedDuration'] = int(mrec[7])
    mrecInfo['duration'] = int(mrec[8])
    mrecInfo['watershed'] = bool(mrec[10])
    mrecInfo['acquisitionDateTime'] = str(time.ctime(int(mrec[16])))
    mrecInfo['acquisitionStatus'] = acqStatus[str(mrec[17])]
    mrecInfo['size'] = int(mrec[21])
    
    return mrecInfo
    
        
    

def recordingEventHandler(eventLocator,status):
    '''
    this event handler is to not recording events
    '''
    eventInfo = getEventInfo(eventLocator)    
    string = None
    if status == RECORDING_BEGUN:
        string = 'Recording Started for %s : Event [%s]'%(eventLocator,eventInfo)
    elif status == RECORDING_ACQUIRED:
        string = 'Recording acquired for %s : Event [%s]'%(eventLocator,eventInfo)
    elif status == RECORDING_PARTIALLY_ACQUIRED:
        string = 'Recording acquired partially for %s : Event [%s]'%(eventLocator,eventInfo)
    elif status == RECORDING_FAILED:
        string = 'Recording Failed for %s : Event [%s]'%(eventLocator,eventInfo)
    printDebug(string)

def bookingListChangeHandler(changes):
    '''
    '''
    string = None
    for booking,status in changes.iteritems():
        
        if status == BOOKING_LIST_ADDED:
            string = 'Booking %s added : Booking Info %s'%(booking,getBookingInfo(booking))
        elif status == BOOKING_LIST_UPDATED:
            string = 'Booking %s Updated'%(booking)
        elif status == BOOKING_LIST_DELETED:
            string = 'Booking %s Deleted'%(booking)
        printDebug(string)
    
def scheduledRecordingListChangeHandler(changes):
    '''
    this event handler is for changes to scheduled recording list
    '''
    
    string = None
    for event,status in changes.iteritems():
        eventInfo = getEventInfo(event)
        if status == RECORDING_LIST_ADDED:
            string = "Scheduled Recording added for Event %s : Event [%s]"%(event,eventInfo)
            schedRec = linearAcq_iface.getScheduledRecordingsByEventLocator(event)
            for count in range(0,len(schedRec)):
                sched_recs.append(schedRec[count])
        elif status == RECORDING_LIST_UPDATED:
            string = "Scheduled Recording Updated for Event %s : Event [%s]"%(event,eventInfo)
        elif status == RECORDING_LIST_DELETED:
            string = "Scheduled Recording Deleted for Event %s : Event [%s]"%(event,eventInfo)
            schedRec = linearAcq_iface.getScheduledRecordingsByEventLocator(event)
            for count in range(0,len(schedRec)):
                sched_recs.remove(schedRec[count]) # assumption is that there will be only one scheduled recording for one event
        printDebug(string)                

def schedRecConflictHandler(eventlocators):
    '''
    this event handler is for scheduled recording conflict
    '''
    printDebug('Scheduled Recording Conflict Detected !!! **** conflicting Recordings:')    
    for event in eventlocators:
        string = "Event Info: %s"%(getEventInfo(event)) 
        printDebug(string) 
         
def tunerExhaustionWarningHandler(eventlocators):
    '''
    this event handler is for Tuner Exhaustion Warning
    '''
    string=None
    printDebug('Tuner Exhaustion Warning Detected !!! **** conflicting Recordings:')    
    for event in eventlocators:
        string = "Event Info: %s"%(getEventInfo(event))
        printDebug(string)
        
def powerStateChangeHandler(newState):
    '''
    Handler for PowerStateChange
    '''
    string = " STB Power State changed to %s"%(powerState[str(newState)])
    printDebug(string)
    
    
        
def presentFollowingChangeHandler(service,eventlocators):
    '''
    Handler to check when events scheduled for recording start
    This handler will get array of present and following events, we check if the event locator for present is in sched_recs list, if yes then recording should start for this event
    '''
    global sched_recs
    string=None
    
    
    if len(eventlocators) != 0:
        present_event = eventlocators[0]        
        for sr in sched_recs:
            schedrecInfo = getSchedRecInfo(sr)
            if schedrecInfo['eventLocator'] == present_event[1]:
                eventInfo = getEventInfo(present_event[1])
                string = 'Event Started : Event [%s]'%(eventInfo)
                printDebug(string)

def libraryContentChangeHandler(changes):
    '''
    function to print mediarecord information when acquisition is complete/failed
    '''
    string = None
    for mr,status in changes.iteritems():
        
        if status == LibraryContentChangeType_ADDED:
            mrec = lml_iface.getMediaRecord(mr)
            mrecInfo = getmediaRecInfo(mrec)
            string = 'Library content added ID %s : Title [%s]'%(mrecInfo['mediaRecordID'],mrecInfo['title'])
        elif status == LibraryContentChangeType_UPDATED:
            mrec = lml_iface.getMediaRecord(mr)
            mrecInfo = getmediaRecInfo(mrec)
            if mrecInfo['acquisitionStatus'] != acqStatus['-1'] and mrecInfo['acquisitionStatus'] != acqStatus['0']:
                # if the acquisition status reports completion of acquisition then pring the mrec information
                string = 'Library content Updated for ID %s : Media Record [%s]'%(mrecInfo['mediaRecordID'],mrecInfo)
        elif status == LibraryContentChangeType_DELETED:
            string = 'Library content deleted ID %s'%(str(mr))
        if string != None:
            printDebug(string)
    # print storage space free space value
    storage_space = lml_iface.getStorageSpace()
    string = 'Current amount of Free space in LML = %s bytes'%(str(storage_space[2]))
                   

def lowStorageSpaceHandler(storageSpace):
    '''
    '''
    string = 'Low Storage Space Signal : StorageSpace - Total bytes used for recording = %s , Free bytes = %s'%(int(storageSpace[0]),int(storageSpace[2]))
    printDebug(string)
    
    
    
        
    
def cleanup():
    printDebug("Cleaning up...")

    

if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    
    global sched_recs
    global mediaRecords
    
    string = None
    # Get the required DBus Objects
    loop = gobject.MainLoop()
    timer_loop = gobject.MainLoop()
    bus=dbus.SessionBus()
    
    linearAcq = bus.get_object('Zinc.ContentAcquisition', '/Zinc/ContentAcquisition/LinearAcquisition')
    eventRepo = bus.get_object('Zinc.MetadataProxy', '/Zinc/Metadata/EventRepository')
    lml = bus.get_object('Zinc.Media', '/Zinc/Media/LocalMediaLibrary')
    pm = bus.get_object('Zinc.System','/Zinc/System/PowerManager')
    linearAcq_iface = dbus.Interface(linearAcq,dbus_interface='Zinc.ContentAcquisition.LinearAcquisition')
    eventRepo_iface = dbus.Interface(eventRepo,dbus_interface='Zinc.Metadata.EventRepository')
    lml_iface = dbus.Interface(lml,dbus_interface='Zinc.Media.LocalMediaLibrary')
    pm_iface = dbus.Interface(pm,dbus_interface='Zinc.System.PowerManager')
    
    
    
    # creating event handlers
    bus.add_signal_receiver(recordingEventHandler, dbus_interface="Zinc.ContentAcquisition.LinearAcquisition", signal_name="RecordingEvent")
    bus.add_signal_receiver(schedRecConflictHandler, dbus_interface="Zinc.ContentAcquisition.LinearAcquisition", signal_name="ScheduledRecordingConflict")
    bus.add_signal_receiver(tunerExhaustionWarningHandler, dbus_interface="Zinc.ContentAcquisition.LinearAcquisition", signal_name="TunerExhaustionWarning")
    bus.add_signal_receiver(bookingListChangeHandler, dbus_interface="Zinc.ContentAcquisition.LinearAcquisition", signal_name="BookingListChange")
    bus.add_signal_receiver(scheduledRecordingListChangeHandler, dbus_interface="Zinc.ContentAcquisition.LinearAcquisition", signal_name="ScheduledRecordingListChange")
    bus.add_signal_receiver(presentFollowingChangeHandler, dbus_interface="Zinc.Metadata.EventRepository", signal_name="PresentFollowingChange")
    bus.add_signal_receiver(libraryContentChangeHandler, dbus_interface="Zinc.Media.LocalMediaLibrary", signal_name="LibraryContentChange")
    bus.add_signal_receiver(powerStateChangeHandler, dbus_interface="Zinc.System.PowerManager", signal_name="PowerStateChange")
    bus.add_signal_receiver(lowStorageSpaceHandler, dbus_interface="Zinc.Media.LocalMediaLibrary", signal_name="LowStorageSpace")
    
    
    
    state = pm_iface.getState()
    
    # Print the current Scheduled Recording List
    sched_recs = linearAcq_iface.getScheduledRecordings()
    count=0
    printDebug("The Current Scheduled Recording List :")
    for sr in sched_recs:
        schedrecInfo = getSchedRecInfo(sr)
        string="Scheduled Recording %s"%(schedrecInfo)
        printDebug(string)
    
    if str(state) == "5":           
        # Print current LML
        mediaRecords = lml_iface.getMediaRecords(0,2,4,True,0,4294967295)
        count=0
        printDebug("The Current MediaRecords List :")
        for mrec in mediaRecords:
            mrecInfo = getmediaRecInfo(mrec)
            string="Media Record %s"%(mrecInfo)
            printDebug(string)
    
    
    try: 
        loop.run()
    except KeyboardInterrupt:
        cleanup()
        sys.exit()
        
    


