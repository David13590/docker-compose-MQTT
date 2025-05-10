# Docker and Docker compose project with mosquitto_MQTT and streamlit 
This project aims to develop a deployable docker environment, that combines a mosquitto broker, 
subscriber and a python program to display temperature readings on a streamlit dashboard.

## Setup and deployment
### Requirements
The requirede programs to run the project. Make sure that these are installed on the host machine.
* Docker
* Docker compose


### Deployment
Clone this repo with: ```git clone  https://github.com/David13590/docker-compose-MQTT.git```

Change directory to the subscriber subfolder: ```cd docker-compose-MQTT/subscriber```  
This folder contains the main docker compose file ```addmqtttodb_Sub_Broker_compose.yaml``` which runs, as of writing this doc(10-05-25), the broker service aswell a the process that adds MQTT messages to the database.  
The second compose file ```addmqtttodb_compose.yaml``` only runs the service to add MQTT messages to the DB. Which is used in tandem the compose file in the ```/broker``` folder in the root of this directory.

Build the main compose file with: ```docker compose -f addmqtttodb_Sub_Broker_compose.yaml up --build ```  

***Flags***  
```-f``` Specifies what compose file to build.  
```--build``` Tells docker to rebuild the image every time the command is run.

Now the there should be running two containers running, ```addMQTTtoDB``` and ```mosquitto_broker```. Check running conatiners with ```docker ps -a```