#!/bin/bash
BROKER_IP=192.168.110.202
TOPIC=esp32/ds/temperature
DATABASE=/home/david/Programming/python/temperature.db
TABLE1=temperature1

while true
do
	#Get MQTT msg
	mosquitto_sub -h "$BROKER_IP" -t "$TOPIC" | while read -r payload
	do
		#Split MQTT output
		sensorName=$(echo "${payload}" | awk '{split($0,outputSensorName,":"); print outputSensorName[1]}')
		temp=$(echo "${payload}" | awk '{split($0,outputTemp,":"); print outputTemp[2]}')
		echo "${sensorName}"
		echo "${temp}"

		#Add to db
		sqlite3 $DATABASE -cmd "INSERT INTO $TABLE1(sensor_name, reading) VALUES('$sensorName', '$temp');" .quit
	done
	sleep 150
done
