progname = "heat2openhab.py"
version = "v0.01"
import sys
import serial
import datetime
import os
import locale
import syslog
from time import sleep
from urllib import request, parse


debug    = 0
comport = "/dev/ttyUSB20"
opehabsrv    = "192.168.15.11"
openhabport   = "8081"

################################################################################################################################################
#postUpdate -- Calls OpenHAB API to update the value of item
################################################################################################################################################
def postUpdate(item, value):
    req = request.Request("http://"+opehabsrv+":"+openhabport+"/rest/items/"+item+"/state", data=str(value).encode('utf-8'))
    req.add_header('Content-Type', 'text/plain')
    req.get_method = lambda: 'PUT'
    resp = request.urlopen(req)
    if resp.status!=202 :
        if debug: print("Response was %s %s" % (resp.status, resp.reason))

################################################################################################################################################
#Main program
################################################################################################################################################
syslog.syslog('Started')
if debug: print('Debug ON')
if debug: print("Python version %s.%s.%s" % sys.version_info[:3])
if debug: print("pySerial version %s" % serial.VERSION)

#Show startup setting
if debug: print ("\r")
if debug: print ("COM port : %s" % comport )

#################################################################################################################################################
#Set COM port config
ser = serial.Serial()
ser.baudrate = 300
ser.bytesize=serial.SEVENBITS
ser.parity=serial.PARITY_EVEN
ser.stopbits=serial.STOPBITS_TWO
ser.xonxoff=0
ser.rtscts=0
ser.timeout=20
ser.port=str(comport)

#sys.exit()
#################################################################
# COM port reading                                              #
#################################################################    
#Open COM port
try:
    ser.open()
except:
    syslog.syslog('Error opening comport ' + comport)
    sys.exit ("Error opening port %s. Script aborted."  % comport)
if debug: print ("Opened com port.")
# Wake up
ser.setRTS(False)
ser.setDTR(False)
sleep(5)
ser.setDTR(True)
ser.setRTS(True)
ir_command=("\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2F\x3F\x21\x0D\x0A")
ser.write(ir_command.encode('utf-8')) 
sleep(1.5)
#Initialize
if debug: print ("Initialisation on 300 baud")
ir_command='/?!\x0D\x0A'
ser.write(ir_command.encode('utf-8'))
ser.flush()
#Wait for initialize confirmation
ir_buffer = ''
while '/LUGC2WR5\r\n' not in ir_buffer:
    ir_buffer = str(ser.readline(), "utf-8")
    if '/?!\x0D\x0A' in ir_buffer:
        ir_buffer = str(ser.readline(), "utf-8")
ir_lines = ir_buffer.strip().split('\r\n')

if debug: print ("Data exchange on 2400 baud")
#Set to 2400baud
ser.baudrate = 2400

#Wait for data
ir_buffer = ''
ETX = False
while not ETX:
    ir_buffer = str(ser.readline(), "utf-8")
    if '\x03' in ir_buffer:
        ETX = True
    #Strip the STX character
    ir_buffer = ir_buffer.replace('\x02','')
    #Strip the ! character
    ir_buffer = ir_buffer.replace('!','')
    #Strip the ETX character
    ir_buffer = ir_buffer.replace('\x03','')
    ir_lines.extend(ir_buffer.strip().split('\r\n'))
if debug: print ("Data transfer completed")
    #Close port and show status
try:
    ser.close()
except:
    syslog.syslog('Error closing comport: ' + ser.port)
    sys.exit ("Error closing %s. Script aborted."  %  ser.port)  

#################################################################
# Process data                                                  #
# Get data from second item in list                             #
################################################################# 
heat_data = ir_lines
if debug: print("Raw Telegram data")
if debug: print(heat_data)
heat_meterreading_energy = float(heat_data[1][heat_data[1].find("6.8(") +4:heat_data[1].find("*",heat_data[1].find("6.8(") +4)])
if debug : print("energy: " + str(heat_meterreading_energy))
heat_meterreading_volume = float(heat_data[1][heat_data[1].find("6.26(") +5:heat_data[1].find("*",heat_data[1].find("6.26(") +5)])
if debug : print("volume: " + str(heat_meterreading_volume))

#################################################################
# Post data to openhab                                          #
#################################################################   
postUpdate("heat_energy", heat_meterreading_energy)
postUpdate("heat_volume", heat_meterreading_volume)
syslog.syslog('Completed succesfully')









