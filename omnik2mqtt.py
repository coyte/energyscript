#!/usr/bin/python
# Python script om Omnik inverter data weer te geven in MQTT
# paho needs to be installed (pip3 install paho-mqtt)
# MQTTBROKER, MQTTPORT, INVERTER1...INVERTERx need to be defined in env (see environment.sh)



import socket
import sys
import syslog
import time
import paho.mqtt.client as paho
import struct

progname = "omnik2mqtt.py"
version = "v0.01"

debug = 0
# add all your inverters below, script will cycle through them and add retrieved values
inverter = [(os.environ.get('INVERTER1')), (os.environ.get('INVERTER2'))]

port = 8899  # default port for inverter


def on_publish(client, userdata, result):  # create function for callback
    print("data published \n")
    pass


client = paho.Client()
client.on_publish = on_publish
client.connect(os.environ.get('MQTTBROKER'), int(os.environ.get('MQTTPORT')))

# ==========================================================================


class InverterMsg(object):
    """Decode the response message from an omniksol inverter."""
    raw_msg = ""

    def __init__(self, msg, offset=0):
        self.raw_msg = msg
        self.offset = offset

    def __get_string(self, begin, end):
        """Extract string from message.

        Args:
            begin (int): starting byte index of string
            end (int): end byte index of string

        Returns:
            str: String in the message from start to end
        """
        return self.raw_msg[begin:end]

    def __get_short(self, begin, divider=10):
        """Extract short from message.

        The shorts in the message could actually be a decimal number. This is
        done by storing the number multiplied in the message. So by dividing
        the short the original decimal number can be retrieved.

        Args:
            begin (int): index of short in message
            divider (int): divider to change short to float. (Default: 10)

        Returns:
            int or float: Value stored at location `begin`
        """
        num = struct.unpack('!H', self.raw_msg[begin:begin + 2])[0]
        if num == 65535:
            return -1
        else:
            return float(num) / divider

    def __get_long(self, begin, divider=10):
        """Extract long from message.

        The longs in the message could actually be a decimal number. By
        dividing the long, the original decimal number can be extracted.

        Args:
            begin (int): index of long in message
            divider (int): divider to change long to float. (Default : 10)

        Returns:
            int or float: Value stored at location `begin`
        """
        return float(
            struct.unpack('!I', self.raw_msg[begin:begin + 4])[0]) / divider

    @property
    def id(self):
        """ID of the inverter."""
        return self.__get_string(15, 31)

    @property
    def temperature(self):
        """Temperature recorded by the inverter."""
        return self.__get_short(31)

    @property
    def power(self):
        """Power output"""
        return self.__get_short(59)

    @property
    def e_total(self):
        """Total energy generated by inverter in kWh"""
        return self.__get_long(71)

    def v_pv(self, i=1):
        """Voltage of PV input channel.

        Available channels are 1, 2 or 3; if not in this range the function will
        default to channel 1.

        Args:
            i (int): input channel (valid values: 1, 2, 3)

        Returns:
            float: PV voltage of channel i
        """
        if i not in range(1, 4):
            i = 1
        num = 33 + (i - 1) * 2
        return self.__get_short(num)

    def i_pv(self, i=1):
        """Current of PV input channel.

        Available channels are 1, 2 or 3; if not in this range the function will
        default to channel 1.

        Args:
            i (int): input channel (valid values: 1, 2, 3)

        Returns:
            float: PV current of channel i
        """
        if i not in range(1, 4):
            i = 1
        num = 39 + (i - 1) * 2
        return self.__get_short(num)

    def i_ac(self, i=1):
        """Current of the Inverter output channel

        Available channels are 1, 2 or 3; if not in this range the function will
        default to channel 1.

        Args:
            i (int): output channel (valid values: 1, 2, 3)

        Returns:
            float: AC current of channel i

        """
        if i not in range(1, 4):
            i = 1
        num = 45 + (i - 1) * 2
        return self.__get_short(num)

    def v_ac(self, i=1):
        """Voltage of the Inverter output channel

        Available channels are 1, 2 or 3; if not in this range the function will
        default to channel 1.

        Args:
            i (int): output channel (valid values: 1, 2, 3)

        Returns:
            float: AC voltage of channel i
        """
        if i not in range(1, 4):
            i = 1
        num = 51 + (i - 1) * 2
        return self.__get_short(num)

    def f_ac(self, i=1):
        """Frequency of the output channel

        Available channels are 1, 2 or 3; if not in this range the function will
        default to channel 1.

        Args:
            i (int): output channel (valid values: 1, 2, 3)

        Returns:
            float: AC frequency of channel i
        """
        if i not in range(1, 4):
            i = 1
        num = 57 + (i - 1) * 4
        return self.__get_short(num, 100)

    def p_ac(self, i=1):
        """Power output of the output channel

        Available channels are 1, 2 or 3; if no tin this range the function will
        default to channel 1.

        Args:
            i (int): output channel (valid values: 1, 2, 3)

        Returns:
            float: Power output of channel i
        """
        if i not in range(1, 4):
            i = 1
        num = 59 + (i - 1) * 4
        return int(self.__get_short(num, 1))  # Don't divide

    @property
    def e_today(self):
        """Energy generated by inverter today in kWh"""
        return self.__get_short(69, 100)  # Divide by 100

    @property
    def h_total(self):
        """Hours the inverter generated electricity"""
        return int(self.__get_long(75, 1))  # Don't divide

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
        msg = InverterMsg(data)

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
