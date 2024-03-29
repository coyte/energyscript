#!/usr/bin/env python3
# Python script om P1 telegram weer te geven in MQTT
# paho needs to be installed (pip3 install paho-mqtt)
# user needs to be member of dialout group (usermod -a -G dialout LOGINNAME)

import serial
import paho.mqtt.client as paho
import time
import syslog
import os
import json

progname = "dsmr2mqtt.py"
version = "v0.01"

def on_publish(client, userdata, result):  # create function for callback
    print("data published \n")
    pass


debug = 0
comport = os.environ.get('DSMRPORT')
#comport = "/dev/serial/by-id/usb-FTDI_P1_Converter_Cable_P1XZ6U1M-if00-port0"


client = paho.Client()
client.on_publish = on_publish
client.connect(os.environ.get('MQTTBROKER'), int(os.environ.get('MQTTPORT')))


##############################################################################
# Main program
##############################################################################
syslog.syslog('Started')
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
    syslog.syslog("Error opening COM port: %s. Aborting." % ser.name)
    sys.exit(1)

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
    syslog.syslog("Cannot close serial port: %s. Aborting." % ser.name)
    sys.exit(1)

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
syslog.syslog("Publishing results ...")
topic = "homeassistant/sensor/dsmr/actual/config"
payload = { "name":"actual",
            "unique_id":"actual",
            "state_topic": "homeassistant/sensor/dsmr/state",
            "value_template":"{{ value_json.actual | is_defined }}",
            "unit_of_meas":"W",
            "device_class":"power",
            "state_class":"measurement",
            "device":{"name":"dsmr","model":"smartmeter","manufacturer":"Kaifa","identifiers":["A4C138C38EE5"]}}
client.publish(topic, json.dumps(payload))

time.sleep(10)

topic = "homeassistant/sensor/dsmr/prod/config"
payload = {"name":"productie",
            "unique_id":"prod",
            "state_topic": "homeassistant/sensor/dsmr/state",
            "value_template":"{{ value_json.prod | is_defined }}",
            "unit_of_meas":"kWh",
            "device_class":"energy",
            "state_class":"total",
            "device":{"name":"dsmr","model":"smartmeter","manufacturer":"Kaifa","identifiers":["A4C138C38EE5"]}}
client.publish(topic, json.dumps(payload))
time.sleep(10)

topic = "homeassistant/sensor/dsmr/cons/config"
payload = { "name":"verbruik",
            "unique_id":"cons",
            "state_topic": "homeassistant/sensor/dsmr/state",
            "value_template":"{{ value_json.cons | is_defined }}",
            "unit_of_meas":"kWh",
            "device_class":"energy",
            "state_class":"total",
            "device":{"name":"dsmr","model":"smartmeter","manufacturer":"Kaifa","identifiers":["A4C138C38EE5"]}}
client.publish(topic, json.dumps(payload))

time.sleep(10)
topic = "homeassistant/sensor/dsmr/state"
data = {"actual":round(actprod-actcons,2),"cons":consumption, "prod":production}
client.publish(topic, json.dumps(data))


#time.sleep(1)

#client.publish("homeassistant/sensor/dsmr/config", '{"name": "dsmr", "device_class": "sensor", "state_topic": "homeassistant/binary_sensor/dsmr/state"}')
#client.publish("homeassistant/sensor/dsmr/actual", actprod-actcons)
#client.publish("homeassistant/sensor/dsmr/cons", consumption)
#client.publish("homeassistant/sensor/dsmr/prod", production)
time.sleep(1)
syslog.syslog('Completed succesfully')
