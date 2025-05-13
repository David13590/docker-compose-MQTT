# Docker and Docker compose project with mosquitto_MQTT and streamlit 
This project aims to develop a deployable docker environment, that combines a mosquitto broker, 
subscriber and a python program to display temperature readings on a streamlit dashboard. Making use of DS18B20 dallas temperature sensors on a esp32.

## Setup and deployment
### Requirements
The required programs to run the project. Make sure that these are installed on the host machine. This doc is written for a debian host, some things may change when building on another OS.
* Docker ([Guide to installing docker and docker compose on debian](https://docs.docker.com/engine/install/debian/))
* Docker compose
* A esp32 with a dallas DS18B20 from which to read the temperature
* Vscode (with platformIO installed) and these libraries:
    * knolleary/PubSubClient
    * paulstoffregen/OneWire
    * milesburton/DallasTemperature

### Deployment
Open Vscode and create a platformIO project, choose the appropriate dev board (I use an Esp32-wroom32 board, so in the board dropdown i thoose **DOIT ESP32 DEVKIT V1**). Add the aforementioned liberaries through the platformIO UI.  

Clone this repo with: ```git clone  https://github.com/David13590/docker-compose-MQTT.git```


From the root folder of the cloned project, copy: ```main.cpp``` to the platformIO src folder. 

In the ```main.cpp``` change: 
* WIFI_SSID: Name of wifi you want the esp to connect to.
* WIFI_PASSWORD: The password of the wifi you want the esp to connect to.
* MQTT_SERVER: To your host machine ip.
* DALLAS_PIN: Change to the gpio pin with the temp sensor. 

Now run the program.  
Pay no mind to the serial monitor error, it will disapear once the compose file is built and started.
___________________________

Change directory to the subscriber subfolder: ```cd subscriber/```  
This folder contains the main docker compose file ```addmqtttodb_Sub_Broker_compose.yaml``` which runs, the broker service, the process that adds MQTT messages to the database, aswell as the script that reads and starts a streamlit dashboard.  
The second compose file ```addmqtttodb_compose.yaml``` only runs the service to add MQTT messages to the DB. Which is used in tandem the compose file in the ```/broker``` folder in the root of this directory.

Open the ```addmqtttemptodb.sh``` file with: ```sudo nano script/addmqtttemptodb.sh```  
Change the broker ip to your host machine ip, the same as in the cpp program.

Build the main compose file with: ```docker compose -f addmqtttodb_Sub_Broker_compose.yaml up --build```  

***Flags***  
```-f``` Specifies what compose file to build.  
```--build``` Tells docker to rebuild the image every time the command is run.

Now the there should be three containers running:   
```addMQTTtoDB```: Subscribes to topics and adds data to DB  
```mosquitto_broker```: Acts as broker service.... thats it.   
```st_dashboard```: Reads the DB and runs a dashboard with streamlit. 

Check running conatiners with ```docker ps -a```
<br>

## Viewing the data
#### Viewing with sqlite3
To manually view the data in the DB, attach to the __addMQTTtoDB__ service with: ```docker exec -it addMQTTtoDB sh```  
The DB is located in: ```/MQTT_database_script/temperature.db``` open it with sqlite3.  

Open the DB with: ```sqlite3 MQTT_database_script/temperature.db``` You are now in the sqlite3 prompt with the DB loaded.
<br>  
List tables in DB: ```.tables```  
View table structure: ```.schema```  
Print all data: ```SELECT * FROM temperature1```  
Print last 100 temp readings: ```SELECT * FROM (SELECT * FROM temperature1 ORDER BY ID DESC LIMIT 100)
ORDER BY ID ASC;```

#### Viewing with the dashboard
To view the dashboard. Open a browser and past this url: ```0.0.0.0:8501```  
The dashboard container also prints the url to terminal.

<br>  

## Adding sensors.
To add a sensor, connect another DS18B20 to the same onewire bus.  
See this guide for adding multiple sensors to the same bus. ([Multiple sensors with onewire](https://lastminuteengineers.com/multiple-ds18b20-arduino-tutorial/))

Navigate to the main cpp program, located the root of the project folder: ```/docker-compose-MQTT/main.cpp```  
Open it with nano, vscode or any text editor. 

To add a sensor:  
Create a new variable of type float: ```float dallasTemp2```  
Give the sensor a name of type string: ```String sensor_name2 = "DS18B20_2"```  

With two sensors added, it would look something like this:
```
// Sensor1
float dallasTemp1;
String sensor_name1 = "DS18B20_1"; 

//Sensor2
float dallasTemp2;
String sensor_name2 = "DS18B20_2"; 
```
<br>

Now add the new sensor variable to the index of dallas sensors. Go to the void loop function, and add the sensor with: ```dallasTemp2 = dallasSensor.getTempCByIndex(1);```  
When adding sensors to the index remeber to increment the index. So sensor1 gets index 0, sensor2 index 1 etc.
```
dallasTemp1 = dallasSensor.getTempCByIndex(0);
dallasTemp2 = dallasSensor.getTempCByIndex(1);
```
<br>
Last is to append the new sensor name and float to the payload. In the loop function, right under the dallas getTempByCIndex, is the MQTT payload this is the message the subscriber receives (the addMQTTtoDB container). Append the new sensor to the the list like so:  

```
String payload = String(sensor_name1) + ":" + String(dallasTemp1) + ":" + String(dallasTemp2) + ":" + String(dallasTemp2);
```
The two last strings is the newly added second sensor. This string gets chopped up by the addMQTTtoDB container with the awk program. Thats why we add semicolons to the payload, to tell awk where to split the message. When adding to the DB, it assumes that every two strings is a name and temperature reading.

All done, save the file and navigate back to: ```cd subscriber/```  
Rebuild the main compose file with: ```docker compose -f addmqtttodb_Sub_Broker_compose.yaml up --build```

## Changing IP-addresses, URL and MQTT topics
To do

## To Do
Add: Streamlit dashboard service to compose file which reads DB.   __DONE!!!__  
Add: Two more temperature sensors which writes to db __PARTIAL! (Added one sensor)__  
Add: Temp two new sensors to streamlit dashboard