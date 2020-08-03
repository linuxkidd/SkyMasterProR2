#!/usr/bin/env python3
"""
SkyMaster R2 Python Processor
by Michael J. Kidd
https://github.com/linuxkidd/pySkyMasterR2


$ ./smpro.py  --help
usage: smpro.py [-h] [-p PORT] [-d {0,1,2}] [-m {0,1,2}] [-b BROKER]
                [-s {0,1}]

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  commuications port descriptor, e.g /dev/ttyUSB0 or
                        COM1
  -d {0,1,2}, --debug {0,1,2}
                        debug data
  -m {0,1,2}, --mqtt {0,1,2}
                        Send to MQTT, 1=Publish, 2=Retain
  -b BROKER, --broker BROKER
                        Hostname or IP of MQTT Broker to which to publish.
  -s {0,1}, --stdout {0,1}
                        Print on StdOut


"""
import serial
import time
import array
import argparse
import signal
import os
import re


def signal_handler(signal, frame):
    print('')
    print('You pressed Ctrl+C!  Exiting...')
    print('')
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    global serial_port
    global printTables
    global mqttc
    global mqttOut
    global pressure
    global wx

    retain=False
    if(mqttOut==2):
        retain=True

    wx={
            'a': {'cmd':10, 'desc':'Version',                 'noun':'version',       'lastVal':'', 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'str' },
            'b': {'cmd':11, 'desc':'Model',                   'noun':'model',         'lastVal':'', 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'str' },
            'c': {'cmd':12, 'desc':'GPS Date (UTC)',          'noun':'utcdate',       'lastVal':'', 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'date' },
            'd': {'cmd':13, 'desc':'GPS Time (UTC)',          'noun':'utctime',       'lastVal':'', 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'time' },
            'e': {'cmd':14, 'desc':'GPS Longitude',           'noun':'gpslng',        'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'lng' },
            'f': {'cmd':15, 'desc':'GPS Latitude',            'noun':'gpslat',        'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'lat'  },
            'g': {'cmd':16, 'desc':'GPS Altitude (M)',        'noun':'gpsalt',        'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'int'  },
            'h': {'cmd':17, 'desc':'GPS Satellites',          'noun':'gpssats',       'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'int'  },
            'i': {'cmd':18, 'desc':'GPS Fixed? ( 1/0 )',      'noun':'gpsfix',        'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'int'  },
            'j': {'cmd':21, 'desc':'Humidity',                'noun':'hum',           'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            'k': {'cmd':22, 'desc':'Absolute Pressure (Hg)',  'noun':'absbaro',       'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            'l': {'cmd':23, 'desc':'Temperature (DegC)',      'noun':'degC',          'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            'm': {'cmd':24, 'desc':'DewPt (DegC)',            'noun':'dewC',          'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            'n': {'cmd':25, 'desc':'SKY Volts',               'noun':'skyV',          'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            'o': {'cmd':26, 'desc':'SKY Lux',                 'noun':'skyLux',        'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            'p': {'cmd':27, 'desc':'P?',                      'noun':'p',             'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            'q': {'cmd':28, 'desc':'SQM Magnitude',           'noun':'sqmMag',        'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            'r': {'cmd':29, 'desc':'SQM Freq(Hz)',            'noun':'sqmFreq',       'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            's': {'cmd':30, 'desc':'SQM Irradiance (uW/cm2)', 'noun':'sqmIrradiance', 'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            't': {'cmd':31, 'desc':'SQM NELM',                'noun':'sqmNELM',       'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            'u': {'cmd':32, 'desc':'u?',                      'noun':'u',             'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            'v': {'cmd':33, 'desc':'Rain sense Volts',        'noun':'rainV',         'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            'w': {'cmd':34, 'desc':'IR Sky Temp (DegC)',      'noun':'irSkyDegC',     'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            'x': {'cmd':35, 'desc':'IR Ambient Temp (DegC)',  'noun':'irAmbDegC',     'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            'y': {'cmd':38, 'desc':'y?',                      'noun':'y',             'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            'z': {'cmd':39, 'desc':'IR Clear Setpoint',       'noun':'irClearSetPt',  'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            'A': {'cmd':40, 'desc':'IR Cloud Setpoint',       'noun':'irCloudSetPt',  'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            'B': {'cmd':44, 'desc':'Wind Speed',              'noun':'wind',          'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            'C': {'cmd':45, 'desc':'Wind Dir',                'noun':'winddir',       'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            'D': {'cmd':49, 'desc':'D?',                      'noun':'D',             'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
            'E': {'cmd':51, 'desc':'E?',                      'noun':'E',             'lastVal':0.0, 'timeout':0, 'lastSent':0.0, 'lastRecv':0.0, 'dataType': 'float', 'delayArray':[], 'avgOver':200, 'delayAvg':0.0 },
        }


    def openPort(serial_port):
        try:
            ser = serial.Serial(serial_port,9600)
            ser.timeout=5
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            return ser
        except:
            print('Error: Failed to open communications port, exiting')
            exit()

    def procSerBuffer(ser):
        tmpline=ser.read(ser.in_waiting).decode('ascii').rstrip()
        time.sleep(0.1)
        starttime=time.time()
        while ser.in_waiting>1 and ( time.time()-starttime < 5 ):
            tmpline+=ser.read(ser.in_waiting).decode('ascii')
            time.sleep(0.1)
        while not tmpline.endswith("$") and ( time.time()-starttime < 5 ):
            tmpline+=ser.read(ser.in_waiting).decode('ascii')
            time.sleep(0.1)
        #print tmpline
        myvals=tmpline.split("$")
        for myval in myvals:
            procLine(myval)

    def getLine(ser):
        tmpline=ser.read_until("$",32)
        #return tmpline.rstrip("$").lstrip()
        print(tmpline)
        return tmpline.decode('ascii').rstrip("$")

    def procLine(line):
        global printOut
        global wx
        if(len(line)<2):
            return

        if line[0] in wx:
            myval=re.sub(r"^.","",line)
            if(wx[line[0]]['dataType']=='float'):
                myval=float(myval)
            elif(wx[line[0]]['dataType']=='int'):
                myval=int(myval)
            elif(wx[line[0]]['dataType']=='lat'):
                if(myval[-1:]=='S'):
                    myval=float(-1*myva[:-1])
                else:
                    myval=float(myval[:-1])
            elif(wx[line[0]]['dataType']=='lng'):
                if(myval[-1:]=='W'):
                    myval=-1*float(myval[:-1])
                else:
                    myval=float(myval[:-1])
            wx[line[0]]['lastVal']=myval
            wx[line[0]]['lastRecv']=time.time()
            if ('delayArray' in wx[line[0]]):
                wx[line[0]]['delayArray'].append(myval)
                if(len(wx[line[0]]['delayArray'])>wx[line[0]]['avgOver']):
                    wx[line[0]]['delayArray'].pop(0)
                wx[line[0]]['delayAvg']=sum(wx[line[0]]['delayArray'])/len(wx[line[0]]['delayArray'])
            if(mqttOut):
                if('delayArray' in wx[line[0]]):
                    mqttc.publish("smpro/"+wx[line[0]]["noun"],'{' + "\"lastVal\": {0:0.6f}, \"delayAvg\": {1:0.6f}, \"avgOver\": {2:d}, \"lastSent\": {3:0.2f}, \"lastRecv\": {4:0.2f}, \"desc\": \"{5:s}\", \"timeout\": {6:d}".format(wx[line[0]]["lastVal"],wx[line[0]]["delayAvg"],len(wx[line[0]]["delayArray"]),wx[line[0]]["lastSent"],wx[line[0]]["lastRecv"], wx[line[0]]["desc"], wx[line[0]]["timeout"])+'}',retain=retain);
                else:
                    mqttc.publish("smpro/"+wx[line[0]]["noun"],'{' + "\"lastVal\": \"{0:s}\", \"lastSent\": {1:0.2f}, \"lastRecv\": {2:0.2f}, \"desc\": \"{3:s}\", \"timeout\": {4:d}".format(str(wx[line[0]]["lastVal"]),wx[line[0]]["lastSent"],wx[line[0]]["lastRecv"], wx[line[0]]["desc"], wx[line[0]]["timeout"])+'}',retain=retain);
            if(printOut):
                if('delayArray' in wx[line[0]]):
                    print("smpro/"+wx[line[0]]["noun"]+': {' + "\"lastVal\": {0:0.6f}, \"delayAvg\": {1:0.6f}, \"avgOver\": {2:d}, \"lastSent\": {3:0.2f}, \"lastRecv\": {4:0.2f}, \"desc\": \"{5:s}\", \"timeout\": {6:d}".format(wx[line[0]]["lastVal"],wx[line[0]]["delayAvg"],len(wx[line[0]]["delayArray"]),wx[line[0]]["lastSent"],wx[line[0]]["lastRecv"], wx[line[0]]["desc"], wx[line[0]]["timeout"])+'}');
                else:
                    print("smpro/"+wx[line[0]]["noun"]+': {' + "\"lastVal\": \"{0:s}\", \"lastSent\": {1:0.2f}, \"lastRecv\": {2:0.2f}, \"desc\": \"{3:s}\", \"timeout\": {4:d}".format(str(wx[line[0]]["lastVal"]),wx[line[0]]["lastSent"],wx[line[0]]["lastRecv"], wx[line[0]]["desc"], wx[line[0]]["timeout"])+'}');
        
    def sendReq(ser):
        mycmd=""
        global wx
        nowtime=time.time()
        for key in sorted (wx):
            if(nowtime-wx[key]['lastSent']>5 and wx[key]['lastRecv']>=wx[key]['lastSent']):
        #        print "{0:s}: Last: {1:f}, Delta: {2:f}".format(wx[key]["noun"],wx[key]["lastSent"],nowtime-wx[key]["lastSent"])
                wx[key]["lastSent"]=nowtime
                ser.write(bytes(":{0:d}$".format(wx[key]['cmd']),"utf-8"))
                mycmd+=":{0:d}$".format(wx[key]['cmd'])
                time.sleep(0.1)
            if(nowtime-wx[key]['lastSent']>15):
        #        print "{0:s}: Last: {1:f}, Delta: {2:f}".format(wx[key]["noun"],wx[key]["lastSent"],nowtime-wx[key]["lastSent"])
                wx[key]["timeout"]+=1
                wx[key]["lastSent"]=nowtime
                ser.write(bytes(":{0:d}$".format(wx[key]['cmd']),"utf-8"))
                mycmd+=":{0:d}$".format(wx[key]['cmd'])
                time.sleep(0.1)
#        if(len(mycmd)):
#            print mycmd
            #ser.write(mycmd)

    def mainLoop():
        ser=openPort(serial_port)
        ser.write(b":10$")
        while True:
            while(ser.in_waiting > 1):
                #print "Serial data waiting: {0:d}".format(ser.in_waiting)
                # myline=getLine(ser)
                # procLine(myline)
                procSerBuffer(ser)
                time.sleep(0.1)
            sendReq(ser)
            time.sleep(0.1)
        ser.close()
    mainLoop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", default = "/dev/ttyUSB0", help="commuications port descriptor, e.g /dev/ttyUSB0 or COM1")
    parser.add_argument("-d", "--debug", default = 0, type=int, choices=[0, 1, 2], help="debug data")
    parser.add_argument("-m", "--mqtt", default = 0, type=int, choices=[0, 1, 2], help="Send to MQTT, 1=Publish, 2=Retain")
    parser.add_argument("-b", "--broker", default = "", help="Hostname or IP of MQTT Broker to which to publish.")
    parser.add_argument("-s", "--stdout", default = 1, type=int, choices=[0, 1], help="Print on StdOut")
    args = parser.parse_args()

    serial_port = args.port
    debug_level = args.debug 
    printOut = args.stdout
    mqttOut = args.mqtt
    mqttBroker = args.broker
    wx={}

    if(mqttOut>0):
        import paho.mqtt.client as mqtt #import the client1
        mqttc = mqtt.Client("skymaster") #create new instance
        mqttClock=0

        try:
            mqttc.connect(mqttBroker, port=1883) #connect to broker
            print("MQTT Broker Connected")
        except:
            print("MQTT Broker Connection Failed")
            exit(1)

    main()

