# energyscript
Scripts read heating and electricity meter and publish the result to Openhab items through API call.
The two scripts basically read the telegram for the meter and use identifiers to get the required data, which is then formatted and send to OpenHAB.

The heat2openhab script deals with a UH50 / 2WR5 heating meter from Landis & Gyr as used by Dutch provider Eneco. To connect to the meter a Volkszahler IR head is used.
The dsmr2openhab script read a DSMR5 (but should be backwards compatible). It reads and consolidates the tariff1 and tariff2 reading into a single variable which is updated to OpenHAB.

The scripts content is stolen and borrowed from a number of examples I found. I adapted and extended them to suit my needs.
The scripts run of a Rasberry Pi 1, started by a cronjob. The scripts need Python v3 and pyserial library. 
The electricity script is ran once every ten minutes, the heating script once per hour (will probably change to once every two hours, to preserve meters battery life). Comport assignment is done by id, not to create udev script.
