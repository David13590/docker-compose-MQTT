# Docker and Docker compose project with mosquitto_MQTT and streamlit 
This project aims to develop a deployable docker environment, that combines a mosquitto broker, 
subscriber and a python program to display temperature readings on a streamlit dashboard. Making use of a DS18B20 dallas temperature sensor on a esp32.

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
* MQTT_SERVER: Is your host machine ip.
* DALLAS_PIN: Change to the gpio pin with the temp sensor. 

Now run the program.  
Pay no mind to the serial monitor error, it will disapear once the compose file is built and started.
___________________________
<br>

Change directory to the subscriber subfolder: ```cd subscriber/```  
This folder contains the main docker compose file ```addmqtttodb_Sub_Broker_compose.yaml``` which runs, the broker service, the process that adds MQTT messages to the database aswell as the script that reads and starts a streamlit dashboard.  
The second compose file ```addmqtttodb_compose.yaml``` only runs the service to add MQTT messages to the DB. Which is used in tandem the compose file in the ```/broker``` folder in the root of this directory.

Open the ```addmqtttemptodb.sh``` file with: ```sudo nano script/addmqtttemptodb.sh```  
Change the broker ip to your host machine ip, the same as in the cpp program.

Build the main compose file with: ```docker compose -f addmqtttodb_Sub_Broker_compose.yaml up --build```  

***Flags***  
```-f``` Specifies what compose file to build.  
```--build``` Tells docker to rebuild the image every time the command is run.

Now the there should be two containers running, ```addMQTTtoDB``` and ```mosquitto_broker```. Check running conatiners with ```docker ps -a```

  
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
If you have setup the secrets.toml file correctly, it is as simple as opening a browser and pasting this url: ```0.0.0.0:8501```  
This server address can be changed in the main compose file: ```addmqtttodb_Sub_Broker_compose.yaml```

<br>  

## Changing IP-addresses and adding sensors.
To do

## To Do
Add: Streamlit dashboard service to compose file which reads DB.   __DONE!!!__  
Add: Two more temperature sensors which writes to db  
Add: Temp sensors to streamlit dashboard