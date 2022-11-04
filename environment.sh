#Copy this file to .envvars and adapt to suit your situation
#Reflect the location of the file in crontab
#MQTT
export MQTTBROKER="mosquitto.example.com"
export MQTTPORT=4321

#Openhab
export OPENHABSERVER="5.6.7.8"
export OPENHABPORT=1234

#Inverter defined by FQDN/IP address and serialno
export INVERTER1="1.2.3.4, 1234567899"
export INVERTER2="1.2.3.5, 1234567899"
export INVERTER3="1.2.3.6, 1234567899"