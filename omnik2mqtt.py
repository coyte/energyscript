#!/usr/bin/python
"""
Omnik2mqtt program.
Get data from an omniksol inverter with 602xxxxx - 606xxxx ans save the data in a database or push to pvoutput.org.
"""

import socket
import sys
import syslog
import time
import InverterMsg  # Import the Msg handler
import paho.mqtt.client as paho

progname = "omnik2mqtt.py"
version = "v0.01"

mqttbroker = "cntr.teekens.info"
mqttport = "1883"
debug = 0
inverter = [("10.0.4.28", 1602031687), ("10.0.4.27", 1602372469)]
port = 8899  # default port for inverter


def on_publish(client, userdata, result):  # create function for callback
    print("data published \n")
    pass


client = paho.Client()
client.on_publish = on_publish
client.connect(mqttbroker, mqttport)


# =========================================================================


def generate_string(serial_no):
    """Create request string for inverter.
    The request string is build from several parts. The first part is a fixed 4 char string the second part is the reversed hex notation of the s/n twice then again a fixed string of two chars a checksum of the double s/n with an offset and finally a fixed ending char.

    Args:
        serial_no(int): Serial number of the inverter

    Returns:
        str: Information request string for inverter
    """
    response = '\x68\x02\x40\x30'

    double_hex = hex(serial_no)[2:] * 2
    if debug:
        print(double_hex)
    hex_list = [double_hex[i:i + 2].decode('hex')
                for i in reversed(range(0, len(double_hex), 2))]
    cs_count = 115 + sum([ord(c) for c in hex_list])
    checksum = hex(cs_count)[-2:].decode('hex')
    response += ''.join(hex_list) + '\x01\x00' + checksum + '\x16'
    return response
# =============================================================================


# Define global variables to accumulatie data
power = 0
e_total = 0
e_today = 0

# Loop over inverters
for tup in inverter:
    #    print(tup)
    ip, sn = tup
    if debug:
        print(ip)
        print(sn)
    # Connect to inverter
    for res in socket.getaddrinfo(ip, port, socket.AF_INET, socket.SOCK_STREAM):
        family, socktype, proto, canonname, sockadress = res
        try:
            inverter_socket = socket.socket(family, socktype, proto)
            inverter_socket.settimeout(10)
            inverter_socket.connect(sockadress)
        except socket.error as msg:
            self.logger.error('Could not open socket')
            self.logger.error(msg)
            sys.exit(1)

        inverter_socket.sendall(generate_string(sn))
        data = inverter_socket.recv(1024)
        inverter_socket.close()
        msg = InverterMsg.InverterMsg(data)

        power = power + msg.power
        e_total = e_total + msg.e_total
        e_today = e_today + msg.e_today
# =======End Reading from inverters=================================================
print("Total actual power: " + str(power))
print("Total yield: " + str(e_total))
print("Yield today: " + str(e_today))


# Post update to MQTT
client.publish("solar/actual", power)
client.publish("solar/total", e_total)
client.publish("solar/today", e_today)
time.sleep(1)
syslog.syslog('Completed succesfully')
