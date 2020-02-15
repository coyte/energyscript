# energyscript
Scripts read heating and electricity meter and publish the result to Openhab items through API call.
The heat2openmap script deals with a UH50 / 2WR5 heating meter from Landis & Gyr as used by Dutch provider Eneco. To connect to the meter a Volkszahler IR head is used.
The dsmr2openhab script read a dsmr 5 (but should work on prior versions as well. it reads and consolidates the tariff1 and tariff2 reading into a single variable which is pushed to openhab.

The scripts content is stolen and borrowed from a number of examples I found. I adapted and extended them to suit my use case.
The scripts run of a Rasberry Pi, started by a cronjob. the electricity script is ran once every ten minutes, the heating script once per hour (will probably change to once every two hours, to preserve meters battery life). Comport assignment is done by id, not to create udev script.
