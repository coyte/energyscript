# energyscript
Scripts to read energy consumption and production.
The scripts get data from dsmr P1 gen4 meter, Kamstrup 403 mbus heat meter (script not ready) and Omnik PV inverters.
They publish a subset of the data to a homeassistant compatible MQTT,for any home automation to pick up and process.
The formatting of the MQTT enables autodiscovery of devices with entities by HomeAssistant.

![missing image](https://github.com/coyte/energyscript/blob/master/dsmr.png) ![missing image](https://github.com/coyte/energyscript/blob/master/pv.png)



Scripts will read values for MQTT broker & port (I'm not usy autentication), PV inverters and possibly more in the future from environment variables. An example file is given in environment.sh. Adapt it to your situation and source the file before running the scripts manually.
If you intend the to run the script through cron, copy this file and name it .envvars. Make sure to reference it correctly in your crontab (see crontab.lst for example)

The dsmr2mqtt.py script assumes a cable to P1 port of the smart meter, a search for P1 cable on Ali will give you a good choice.

![missing image](https://github.com/coyte/energyscript/blob/master/p1cable.png)


The omnik2mqtt.py script assumes an IP address and serialnumber for each inverter, add them as INVERTERx variables to the .envvars or environment files. The script will cycle through the inverters and sum the power, daily and total energy values from the inverters before outputting them to MQTT.

The heat2mqtt.py script assumes a USB to Mbus master module to be connected. Again look at Aliexpress to get one, price range EUR30-40

![missing image](https://github.com/coyte/energyscript/blob/master/mbus.png)


There still are a few scripts that publish information to OpenHAB. I'm moving off OH and will not be maintaining them.

The scripts run of a Rasberry Pi with Ubuntu 22.04.1 LTS. They are started by a (ordinary user) cronjob. See crontab.lst for entries. The scripts need python 2.7 and python 3.x. Have both installed, and install pyserial and paho-mqtt libraries for both. Comport assignment is done by id, not to create udev script. You may have to change the id in the script (this should be in the external .envvars too)

The scripts content is stolen and borrowed from a number of examples I found. I adapted and extended them to suit my needs.
