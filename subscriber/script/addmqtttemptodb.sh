#!/bin/bash
BROKER_IP=192.168.110.202
TOPIC=esp32/ds/temperature
DATABASE=/MQTT_database_script/temperature.db
TABLE1=temperature1

while true
do
	#Get MQTT msg
	mosquitto_sub -h "$BROKER_IP" -t "$TOPIC" | while read -r payload
	do
		#Split MQTT output
		#Sensor1
		sensorName1=$(echo "${payload}" | awk '{split($1,outputSensorName1,":"); print outputSensorName1[1]}')
		temp1=$(echo "${payload}" | awk '{split($1,outputTemp1,":"); print outputTemp1[2]}')
		echo "${sensorName1}"
		echo "${temp1}"

		#Sensor2
		sensorName2=$(echo "${payload}" | awk '{split($2,outputSensorName2,":"); print outputSensorName2[1]}')
		temp2=$(echo "${payload}" | awk '{split($2,outputTemp2,":"); print outputTemp2[2]}')
		echo "${sensorName2}"
		echo "${temp2}"
		
		#Sensor3
		sensorName3=$(echo "${payload}" | awk '{split($3,outputSensorName3,":"); print outputSensorName3[1]}')
		temp3=$(echo "${payload}" | awk '{split($3,outputTemp3,":"); print outputTemp3[2]}')
		echo "${sensorName3}"
		echo "${temp3}"
		
		#Add to db
		#Sensor1
		sqlite3 $DATABASE -cmd "INSERT INTO $TABLE1(sensor_name, reading) VALUES('$sensorName1', '$temp1');" .quit
		
		#Sensor2
		sqlite3 $DATABASE -cmd "INSERT INTO $TABLE1(sensor_name, reading) VALUES('$sensorName2', '$temp2');" .quit
		
		#Sensor3
		sqlite3 $DATABASE -cmd "INSERT INTO $TABLE1(sensor_name, reading) VALUES('$sensorName3', '$temp3');" .quit
	done
	sleep 300
done
