progname = "smartmeter2openhab.py"
version = "v0.01"
import sys
import serial
import datetime
import os
import locale
from time import sleep
import argparse
import serial.tools.list_ports
from urllib import request, parse
#import random

ecomport = "/dev/ttyUSB10"
hcomport = "/dev/ttyUSB20"
ohsrv    = "192.168.15.11"
ohport   = "8081"

"""
def scan_serial():
#  scan for available ports. return a list of tuples (name, description)
    available = []
    for i in serial.tools.list_ports.comports():
        available.append((i[0], i[1]))
    return available
"""
"""    
################
#Error display #
################
def show_error():
    ft = sys.exc_info()[0]
    fv = sys.exc_info()[1]
    print("Fout type: %s" % ft )
    print("Fout waarde: %s" % fv )
    return
"""

"""
################
#Scherm output #
################
def print_heat_telegram():
    print ("---------------------------------------------------------------------------------------")
    print ("Landis & Gyr UH50 telegram ontvangen op: %s" % heat_timestamp)
    print ("Meter fabrikant/type: Landis & Gyr Ultraheat 50")
    print (" 0. 0 - Meter identificatie: %s" % heat_equipment_id )
    print (" 6. 8 - Meterstand Energie: %0.3f %s" % (heat_meterreading_energy, heat_unitmeterreading_energy) )
    print (" 6.26 - Meterstand Volume: %0.3f %s" % (heat_meterreading_volume, heat_unitmeterreading_volume) )
    print (" 6.31 - Meterstand Gebruiksduur: %0.3f %s" % (heat_meterreading_hours, heat_unitmeterreading_hours) )    
    print ("Einde UH50 telegram" )
    return        
"""
def postUdpate(item, value):
    #print ("http://"+args.server+":"+args.port+"/rest/items/"+item+"/state")
    #print (str(value).encode('utf-8'))
    req =  request.Request("http://"+args.server+":"+args.port+"/rest/items/"+item+"/state", data=str(value).encode('utf-8'))
    req.add_header('Content-Type', 'text/plain')
    req.get_method = lambda: 'PUT'
    resp = request.urlopen(req)
    #if resp.status!=202 :
    #    print("Response was %s %s" % (resp.status, resp.reason))

################################################################################################################################################
#Main program
################################################################################################################################################
#print ("Landis & Gyr IR Datalogger %s" % version)
equipment_prefix = "UH50"
comport=0
output_mode="scherm"
win_os = (os.name == 'nt')
if win_os:
    print("Windows Mode")
else:
    print("Non-Windows Mode")
print("Python versie %s.%s.%s" % sys.version_info[:3])
print("pySerial version %s" % serial.VERSION)
print ("Control-C om af te breken")

################################################################################################################################################
#Commandline arguments parsing
################################################################################################################################################    
parser = argparse.ArgumentParser(prog=progname, description='energylogger', epilog="Copyright (c) 2020 Niels Teekens")
parser.add_argument("-c", "--comport", help="COM-port name (COMx or /dev/...) that identifies the port your IR-head is connected to")
parser.add_argument("-o", "--output", help="Output mode, default='screen'", default='screen', choices=['screen', 'silent'])
parser.add_argument("-s", "--server", help="openhab server")
parser.add_argument("-p", "--port", help="OpenHAB server port")
#parser.add_argument("-t", "--testing", help="Use dummy data, do not read from IR head')
args = parser.parse_args()

if args.comport == None:
    parser.print_help()
    print ("\r")
    print("%s: error: The following arguments are required: -c/--comport." % progname)
    if win_os:
        print("Available ports for argument -c/--comport:") 
        for n,s in scan_serial():
            print ( n, " - ", s )
    else:
        print("Allowed values for argument -c/--comport: Any '/dev/....' string that identifies the port your P1CC is connected to.") 
    print ("Program aborted.")
    sys.exit()
comport = args.comport
  
output_mode = args.output

#Show startup arguments
print ("\r")
print ("Startup parameters:")
print ("Output mode        : %s" % args.output)
print ("OpenHAB server     : %s" % args.server)
print ("OpenHAB port       : %s" % args.port)

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
ser.port=str(args.comport)
print ("COM-port           : %s" % args.comport )



#################################################################
# COM port reading                                              #
#################################################################    
#Open COM port
try:
    ser.open()
except:
    sys.exit ("Fout bij het openen van %s. Programma afgebroken."  % comport)
print ("Activatie poort.")
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
print ("Initialisatie op 300 baud")
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

print ("Gegevensuitwisseling op 2400 baud")
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
print ("Gegevensuitwisseling voltooid")
    #Close port and show status
try:
    ser.close()
except:
    if win_os:
        sys.exit ("Fout bij het sluiten van %s. Programma afgebroken."  % ser.name)
    else:
        sys.exit ("Fout bij het sluiten van %s. Programma afgebroken."  %  port)  

#################################################################
# Process data                                                  #
#################################################################           
#print ("Number of received elements: %d" % len(ir_lines))
#print ("Array of received elements: %s" % ir_lines)

heat_timestamp=datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d %H:%M:%S" )
heat_data = ir_lines
num_elements = len(ir_lines)
#print("Number of elements: %d"% num_elements)
#parse all heat_data elements

i=0
while i<num_elements:
    #print("Elements index: %d"% i)
    heat_element = heat_data[i]
    #print(heat_element)
    
    if heat_element.find("0.0(")!=-1:
    #heat_equipment_id 
    #0.0(11 digits C/N)
        heat_num_start=heat_element.find("0.0(")+4
        heat_num_end=heat_element.find(")",heat_num_start)
        heat_equipment_id = equipment_prefix + "_" + heat_element[heat_num_start:heat_num_end]

    if heat_element.find("6.8(")!=-1:
    #heat_meterreading_energy, heat_unitmeterreading_energy
    #6.8(Energy * unit)
        heat_num_start = heat_element.find("6.8(") +4
        heat_num_end=heat_element.find("*",heat_num_start)
        heat_meterreading_energy = float(heat_element[heat_num_start:heat_num_end])
        heat_num_start = heat_num_end+1
        heat_num_end=heat_element.find(")",heat_num_start)
        heat_unitmeterreading_energy = heat_element[heat_num_start:heat_num_end]

    if heat_element.find("6.26(")!=-1:
    #heat_meterreading_volume, heat_unitmeterreading_volume
    #6.26(Volume * m3)
        heat_num_start = heat_element.find("6.26(") +5
        heat_num_end=heat_element.find("*",heat_num_start)
        heat_meterreading_volume = float(heat_element[heat_num_start:heat_num_end])
        heat_num_start = heat_num_end+1
        heat_num_end=heat_element.find(")",heat_num_start)
        heat_unitmeterreading_volume = heat_element[heat_num_start:heat_num_end]

    if heat_element.find("6.31(")!=-1:
    #heat_meterreading_hours, heat_unitmeterreading_hours
    #6.31(Hours * h)
        heat_num_start = heat_element.find("6.31(") +5
        heat_num_end=heat_element.find("*",heat_num_start)
        heat_meterreading_hours = float(heat_element[heat_num_start:heat_num_end])
        heat_num_start = heat_num_end+1
        heat_num_end=heat_element.find(")",heat_num_start)
        heat_unitmeterreading_hours = heat_element[heat_num_start:heat_num_end]
     
    i+=1

#################################################################
# Output based on startup parameter 'output_mode'               #
#################################################################   
#heat_meterreading_energy = random.randint(100000,2000000)
#Output to scherm
#if output_mode=="screen": print_heat_telegram()
postUdpate("test", heat_meterreading_energy)










