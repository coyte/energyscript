#!/usr/bin/env python
# Python script om P1 telegram weer te geven

import datetime
import re
import serial
import paho.mqtt.client as paho
import sys
import time

broker = "cntr.teekens.info"
port = 1883


def on_publish(client, userdata, result):  # create function for callback
    print("data published \n")
    pass


client1 = paho.Client("control1")  # create client object
client1.on_publish = on_publish  # assign function to callback
client1.connect(broker, port)  # establish connection

# Seriele poort confguratie
ser = serial.Serial()

# DSMR 4.0/4.2 > 115200 8N1:
ser.baudrate = 115200
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE

ser.xonxoff = 0
ser.rtscts = 0
ser.timeout = 12
ser.port = "/dev/ttyUSB0"
ser.close()


# /KFM5KAIFA-METER
# 1-3:0.2.8(42)
# 0-0:1.0.0(220929142430S)
# 0-0:96.1.1(4530303039313030303037363734373134)
# 1-0:1.8.1(019421.455*kWh)
# 1-0:1.8.2(017121.926*kWh)
# 1-0:2.8.1(006267.981*kWh)
# 1-0:2.8.2(014869.076*kWh)
# 0-0:96.14.0(0002)
# 1-0:1.7.0(00.000*kW)
# 1-0:2.7.0(00.729*kW)
# 0-0:96.7.21(00010)
# 0-0:96.7.9(00005)
# 1-0:99.97.0(2)(0-0:96.7.19)(190629113540S)(0000005474*s)(000101000001W)(2147483647*s)
# 1-0:32.32.0(00000)
# 1-0:32.36.0(00000)
# 0-0:96.13.1()
# 0-0:96.13.0()
# 1-0:31.7.0(003*A)
# 1-0:21.7.0(00.000*kW)
# 1-0:22.7.0(00.729*kW)
#!1D28

while True:
    ser.open()
    checksum_found = False

    while not checksum_found:
        telegram_line = ser.readline()  # Lees een seriele lijn in.
        telegram_line = telegram_line.decode(
            'ascii').strip()  # Strip spaties en blanke regels

        # print(telegram_line)  # debug

        # 1-0:1.7.0 = Actueel laag tarief verbruik in W
        if re.match(b'(?=1-0:1.7.0)', telegram_line):
            lw = telegram_line[10:-4]  # Knip het kW gedeelte eruit (0000.54)
            # vermengvuldig met 1000 voor conversie naar Watt (540.0)
            laagwatt = float(lw) * 1000
        # watt = int(watt) # rond float af naar heel getal (540)

        if re.match(b'(?=1-0:2.7.0)', telegram_line):  # 1-0:1.7.0 = Actueel verbruik in kW
            # 1-0:1.7.0(0000.54*kW)
            hw = telegram_line[10:-4]  # Knip het kW gedeelte eruit (0000.54)
            # vermengvuldig met 1000 voor conversie naar Watt (540.0)
            hoogwatt = float(hw) * 1000
        # watt = int(watt) # rond float af naar heel getal (540)

        # 1-0:1.8.1 - Hoog tarief / 1-0:1.8.1(13579.595*kWh)
        if re.match(b'(?=1-0:1.8.1)', telegram_line):
            # Knip het kWh gedeelte eruit (13579.595)
            kwh1 = telegram_line[10:-5]

        # 1-0:1.8.2 - Laag tarief / 1-0:1.8.2(14655.223*kWh)
        if re.match(b'(?=1-0:1.8.2)', telegram_line):
            # Knip het kWh gedeelte eruit (14655.223)
            kwh2 = telegram_line[10:-5]

        # 1-0:2.8.1 - Teruglevering Laag Tarief / 1-0:1.8.1(13579.595*kWh)
        if re.match(b'(?=1-0:2.8.1)', telegram_line):
            # Knip het kWh gedeelte eruit (13579.595)
            tkwh1 = telegram_line[10:-5]

        # 1-0:2.8.2 - Teruglevering hoog tarief / 1-0:1.8.2(14655.223*kWh)
        if re.match(b'(?=1-0:2.8.2)', telegram_line):
            # Knip het kWh gedeelte eruit (14655.223)
            tkwh2 = telegram_line[10:-5]

        # Check wanneer het uitroepteken ontavangen wordt (einde telegram)
        if re.match(b'(?=!)', telegram_line):
            checksum_found = True

    ser.close()


######################################
# MQTT PUBLISH
######################################

    #print("elektra/actueel_laag " + str(laagwatt) + "\n")
    client1.publish("elektra/actueel_laag", laagwatt)
    #print("elektra\actueel_hoog " + str(hoogwatt) + "\n")
    client1.publish("elektra/actueel_hoog", hoogwatt)
    #print("elektra\kwh_hoog " + str(kwh1) + "\n")
    client1.publish("elektra/kwh_hoog", kwh1)
    #print("elektra\kwh_laag " + str(kwh2) + "\n")
    client1.publish("elektra/kwh_laag", kwh2)
    #print("elektra\Tkwh_hoog " + str(tkwh2) + "\n")
    client1.publish("elektra/tkwh_hoog", tkwh2)
    #print("elektra\Tkwh_laag " + str(tkwh1) + "\n")
    client1.publish("elektra/tkwh_laag", tkwh1)

    time.sleep(1)
    sys.exit()
