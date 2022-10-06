# energyscript
Script to read energy consumption and production from PV.
The scripts get data from dsmr P1 gen4 meter, Kamsterup 403 mbus heat meter, Omnik PV inverters
They publish a subset of the data to MQTT, for any home automation to pick up and process.

There still are a few scripts that publish information to OpenHAB. I'm moving off OH and will not be maintaining them.

The scripts run of a Rasberry Pi, started by a cronjob. The scripts need Python, pyserial and paho-mqtt library. 
Comport assignment is done by id, not to create udev script.

The scripts content is stolen and borrowed from a number of examples I found. I adapted and extended them to suit my needs.
