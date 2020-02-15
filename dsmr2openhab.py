progname = "dsmr2openhab.py"
version = "v0.01"
import sys
import serial
import syslog
from urllib import request, parse

debug       = 0
comport     = "/dev/serial/by-id/usb-FTDI_P1_Converter_Cable_P1XZ6U1M-if00-port0"
opehabsrv   = "ip-address-openhab-server"
openhabport = "port-of-openhab-server"

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

##############################################################################
#Main program
##############################################################################
syslog.syslog('Started')
if debug: print ("Dutch Smart Meter P1 reader",  version)
if debug: print ("Used comport: " + comport)
#Set COM port config
ser = serial.Serial()
ser.baudrate = 115200
ser.bytesize=serial.EIGHTBITS
ser.parity=serial.PARITY_NONE
ser.stopbits=serial.STOPBITS_ONE
ser.xonxoff=0
ser.rtscts=0
ser.timeout=20
ser.port=comport

#Open COM port
try:
    ser.open()
except:
    sys.exit ("Error opening COM port: %s. Aborting."  % ser.name)      


#Cycle through the read lines of the P1 telegram
for lineread in range(0, 23): 
#p1_teller=0
#while p1_teller < 24:
    p1_line=''
    #Read 1 line 
    try:
        p1_raw = ser.readline()
    except:
        sys.exit ("Cannot read %s . Aborting." % ser.name )      
    p1_str=str(p1_raw)
    p1_line=p1_str.strip()

    if p1_line.find("1-0:1.8.1")!=-1 :
        t1consumption = float(p1_line[p1_line.find("1-0:1.8.1(")+10 : p1_line.find("*")])

    if p1_line.find("1-0:1.8.2")!=-1 :
        t2consumption = float(p1_line[p1_line.find("1-0:1.8.2(")+10 : p1_line.find("*")])

    if p1_line.find("1-0:2.8.1")!=-1 :
        t1production = float(p1_line[p1_line.find("1-0:2.8.1(")+10 : p1_line.find("*")])

    if p1_line.find("1-0:2.8.2")!=-1 :
        t2production = float(p1_line[p1_line.find("1-0:2.8.2(")+10 : p1_line.find("*")])

    if p1_line.find("1-0:1.7.0")!=-1 :
        actcons = float(p1_line[p1_line.find("1-0:1.7.0(")+10 : p1_line.find("*")])

    if p1_line.find("1-0:2.7.0")!=-1 :
        actprod = float(p1_line[p1_line.find("1-0:2.7.0(")+10 : p1_line.find("*")])

    if debug: print (p1_line)

#Close port and show status
try:
    ser.close()
except:
    sys.exit ("Cannot close serial port %s. Aborting" % ser.name )   

consumption=round(t1consumption+t2consumption,2)
production=round(t1production+t2production,2)
actprod=actprod*1000
actcons=actcons*1000

if debug: print("t1consumption:      " + str(t1consumption))
if debug: print("t2consumption:      " + str(t2consumption))
if debug: print("t1production:       " + str(t1production))
if debug: print("t2production:       " + str(t2production))
if debug: print("consumption:        " + str(consumption))
if debug: print("production:         " + str(production))
if debug: print("actual consumption: " + str(actcons))
if debug: print("actual production:  " + str(actprod))

postUpdate("ElectricityMeter_ElectriciteitVerbruik", consumption)
postUpdate("ElectricityMeter_ElectriciteitProductie", production)
postUpdate("ElectricityMeter_ElectriciteitHuidigVerbruik", actcons)
postUpdate("ElectricityMeter_ElectriciteitHuidigeProductie", actprod)
syslog.syslog('Completed succesfully')
