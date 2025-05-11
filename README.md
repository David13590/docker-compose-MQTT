# Docker and Docker compose project with mosquitto_MQTT and streamlit 
This project aims to develop a deployable docker environment, that combines a mosquitto broker, 
subscriber and a python program to display temperature readings on a streamlit dashboard. Making use of a DS18B20 dallas temperature sensor on a esp32.

## Setup and deployment
### Requirements
The requirede programs to run the project. Make sure that these are installed on the host machine.
* Docker
* Docker compose
* A esp32 with a dallas DS18B20 from which you read the temperature
* Vscode (with platformIO istalled) and these libraries:
    * knolleary/PubSubClient
    * paulstoffregen/OneWire
    * milesburton/DallasTemperature

### Deployment
Open Vscode and create a platformIO project, choose the aporopriate dev board (I use an Esp32-wroom32 board, so in the board dropdown i thoose **DOIT ESP32 DEVKIT V1**). Add the aforementioned liberaries through the platformIO UI.  

Clone this repo with: ```git clone  https://github.com/David13590/docker-compose-MQTT.git```


From the root folder of the cloned project, copy: ```main.cpp``` to the platformIO src folder. 

In the ```main.cpp``` change: 
* WIFI_SSID: Name of wifi you want the esp to connect to.
* WIFI_PASSWORD: The password of the wifi you want the esp to connect to.
* MQTT_SERVER: Is your host machine ip.
* DALLAS_PIN: Change to the gpio pin with the temp sensor. 

Now run the program.
___________________________
<br>

Change directory to the subscriber subfolder: ```cd subscriber/```  
This folder contains the main docker compose file ```addmqtttodb_Sub_Broker_compose.yaml``` which runs, as of writing this doc(10-05-25), the broker service aswell a the process that adds MQTT messages to the database.  
The second compose file ```addmqtttodb_compose.yaml``` only runs the service to add MQTT messages to the DB. Which is used in tandem the compose file in the ```/broker``` folder in the root of this directory.

Open the ```addmqtttemptodb.sh``` file with: ```sudo nano script/addmqtttemptodb.sh```  
Change the broker ip to your host machine ip, the same as in the cpp program.

Build the main compose file with: ```docker compose -f addmqtttodb_Sub_Broker_compose.yaml up --build ```  

***Flags***  
```-f``` Specifies what compose file to build.  
```--build``` Tells docker to rebuild the image every time the command is run.

Now the there should be two containers running, ```addMQTTtoDB``` and ```mosquitto_broker```. Check running conatiners with ```docker ps -a```