# energyscript
Scripts to read energy consumption and production from PV.
The scripts get data from dsmr P1 gen4 meter, Kamsterup 403 mbus heat meter (not ready), Omnik PV inverters
They publish a subset of the data to MQTT, in a homeassistant compatible way,for any home automation to pick up and process.

There still are a few scripts that publish information to OpenHAB. I'm moving off OH and will not be maintaining them.

The scripts run of a Rasberry Pi with Ubuntu 22.04.1 LTS. They are started by a (ordinary user) cronjob. See crontab.lst for entries. The scripts need Python, pyserial and paho-mqtt libraries to run. Comport assignment is done by id, not to create udev script. 

The scripts content is stolen and borrowed from a number of examples I found. I adapted and extended them to suit my needs.
