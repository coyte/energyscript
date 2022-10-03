#!/usr/bin/env python
# Python script om P1 telegram weer te geven

import datetime
import re
import serial
import paho.mqtt.client as paho
import sys
import time

#from urllib import request
#import parse
import syslog
#import sys

progname = "dsmr2mqtt.py"
version = "v0.01"


def on_publish(client, userdata, result):  # create function for callback
    print("data published \n")
    pass


debug = 0
comport = "/dev/serial/by-id/usb-FTDI_P1_Converter_Cable_P1XZ6U1M-if00-port0"
mqttbroker = "cntr.teekens.info"
mqttport = "1883"

client = paho.Client()
client.on_publish = on_publish
client.connect(mqttbroker, mqttport)


##############################################################################
# Main program
##############################################################################
syslog.syslog('dsmr2mqtt started')
if debug:
    print("Dutch Smart Meter P1 reader",  version)
if debug:
    print("Used comport: " + comport)
# Set COM port config
ser = serial.Serial()
ser.baudrate = 115200
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
ser.xonxoff = 0
ser.rtscts = 0
ser.timeout = 20
ser.port = comport

# Open COM port
try:
    ser.open()
except:
    sys.exit("Error opening COM port: %s. Aborting." % ser.name)


# Cycle through the read lines of the P1 telegram
for lineread in range(0, 23):
    # p1_teller=0
    # while p1_teller < 24:
    p1_line = ''
    # Read 1 line
    try:
        p1_raw = ser.readline()
    except:
        sys.exit("Cannot read %s . Aborting." % ser.name)
    p1_str = str(p1_raw)
    p1_line = p1_str.strip()

    if p1_line.find("1-0:1.8.1") != -1:
        t1consumption = float(
            p1_line[p1_line.find("1-0:1.8.1(")+10: p1_line.find("*")])

    if p1_line.find("1-0:1.8.2") != -1:
        t2consumption = float(
            p1_line[p1_line.find("1-0:1.8.2(")+10: p1_line.find("*")])

    if p1_line.find("1-0:2.8.1") != -1:
        t1production = float(
            p1_line[p1_line.find("1-0:2.8.1(")+10: p1_line.find("*")])

    if p1_line.find("1-0:2.8.2") != -1:
        t2production = float(
            p1_line[p1_line.find("1-0:2.8.2(")+10: p1_line.find("*")])

    if p1_line.find("1-0:1.7.0") != -1:
        actcons = float(p1_line[p1_line.find(
            "1-0:1.7.0(")+10: p1_line.find("*")])

    if p1_line.find("1-0:2.7.0") != -1:
        actprod = float(p1_line[p1_line.find(
            "1-0:2.7.0(")+10: p1_line.find("*")])

    if debug:
        print(p1_line)

# Close port and show status
try:
    ser.close()
except:
    sys.exit("Cannot close serial port %s. Aborting" % ser.name)

consumption = round(t1consumption+t2consumption, 2)
production = round(t1production+t2production, 2)
actprod = actprod*1000
actcons = actcons*1000

if debug:
    print("t1consumption:      " + str(t1consumption))
    print("t2consumption:      " + str(t2consumption))
    print("t1production:       " + str(t1production))
    print("t2production:       " + str(t2production))
    print("consumption:        " + str(consumption))
    print("production:         " + str(production))
    print("actual consumption: " + str(actcons))
    print("actual production:  " + str(actprod))
    print("Atual:              " + str(actprod-actcons))

######################################
# MQTT PUBLISH
######################################
if debug:
    print("Publishing....")
client.publish("dsmr/actual", actprod-actcons)
client.publish("dsmr/cons", consumption)
client.publish("dsmr/prod", production)
time.sleep(1)
syslog.syslog('Completed succesfully')
