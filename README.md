# Docker and Docker compose project with mosquitto_MQTT and Node-red 
This project aims to develop a deployable docker environment, that combines a mosquitto broker, 
subscriber and a python program to display temperature readings on a Node-red dashboard. Making use of DS18B20 dallas temperature sensors on a esp32.

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
Pay no mind to the serial monitor error, it will disappear once the compose file is built and started.
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
```node-red```: Reads the DB and runs a dashboard with Node-red. 

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
To view the dashboard. Open a browser and past this url: ```http://127.0.0.1:1880/ui/```  
The dashboard container also prints the url the flow (where you edit the dashboard) to terminal.

<br>  

## Adding sensors.
To add a sensor, connect another DS18B20 to the same onewire bus.  
See this guide for adding multiple sensors to the same bus. ([Multiple sensors with onewire](https://lastminuteengineers.com/multiple-ds18b20-arduino-tutorial/))

Three files must be modified to add sensors to the system.
- ```main.cpp```
- ```addmqtttemptodb.sh```
- ```flows.json```

We will go through each file below.


### Adding sensors: main.cpp
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
String payload = String(sensor_name1) + ":" + String(dallasTemp1) + " " + String(sensor_name2) + ":" + String(dallasTemp2);
```
The two last strings is the newly added second sensor. This string gets chopped up by the addMQTTtoDB container with the awk program. Thats why we add semicolons and spaces to the payload, to tell awk where to split the message. When adding to the DB, it assumes that every space signals a new name and temperature reading.

With two sensors the payload should print like this. Note the space between the first temperature and second name:
```DS18B20_1:22.00 DS18B20_2:22.13```  

The awk program splits the message into seperate strings. It counts every space as a new string so: ```DS18B20_1:22.00``` is string 1 and ```DS18B20_2:22.13```is string 2.  With that in mind. Now to the next step.

---

### Adding sensors: addmqtttempdb.sh
Open the script folder: ```/docker-compose-MQTT/subscriber/script/```  
Open the sh file: ```sudo nano addmqtttemptodb.sh``` (Or use geany to open the file. A text editor with a more conventional control scheme)

In the second do loop, you will se two variables and echo's for each variable. The echo's are just so we can see the values when the docker container is running. The variables are where we split each received MQTT messege. The awk split for the first sensor is this:
```
sensorName1=$(echo "${payload}" | awk '{split($1,outputSensorName1,":"); print outputSensorName1[1]}')
```

The awk program works like this:
```
awk '{split($0, array, ":")}'
            \/  \___/  \_/
            |     |     |
        string    |     delimiter
                  |
                array to store the pieces
```
When adding a new sensor copy the previous sonsor awk command, so with sensor2 added:
```
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
```

Increment the string in the split command. Sensor1 gets string1: ```$1```and sensor2 ```$2```, see below.     
```
awk '{split($2,outputSensorName2,":");}'
            \/  
            |        
        Increment this                      
```
This is also where the space in the payload comes into play. When chosing a string with ```$1```or ```$2```, evey space in the message is a new string. So taking a look a the received payload:
```
DS18B20_1:22.00 DS18B20_2:22.13
\____________/ \/ \___________/
    |           |    |
String1 $1      |   String2 $2
                Space
```
With a string selected, we can now get the name and temp reading by printing either the left of the semicolon or the right.
In the print section of the awk command: ```print outputSensorName2[1]``` modify the number in the brackets, either 1 or 2. 

Selecting ```[1]``` would turn string1: ```DS18B20_2:22.13``` into: ```DS18B20_2```  

Selecting ```[2]``` would turn string2: ```DS18B20_2:22.13``` into:
```22.13```

So to get the name and temperature of the newly added sensor2: 
```
sensorName2=$(echo "${payload}" | awk '{split($2,outputSensorName2,":"); print outputSensorName2[1]}')
temp2=$(echo "${payload}" | awk '{split($2,outputTemp2,":"); print outputTemp2[2]}')
```
Last is to add the two new variables, the sensor name and reading to the DB.
```sqlite3 $DATABASE -cmd "INSERT INTO $TABLE1(sensor_name, reading) VALUES('$sensorName2', '$temp2');" .quit```  
Replacing variables in the VALUES field with the variables of the new sensor.

You are now done with this file. Save and exit

---
### Adding sensors: Modifying Node-red dashboard (flows.json)
Make sure the main docker compose file is running. If not.  
Run the docker compose file: ```docker compose -f addmqtttodb_Sub_Broker_compose.yaml up --build```  

Open the Node-red flow editor in a browser window: ```127.0.0.1:1880```  

In the Node-red editor copy the ```sensor1``` sql node and ```Set topic sensor1``` node.  
Connect the input of the new sensor to the ```refresh data``` node and the output to the newly copied topic node. Connect the topic node the the ```Join sensor payloads```  

Doubleclick the sql sensor node, changing the name and sql statement to match the new sensor: ```SELECT * FROM temperature1 WHERE sensor_name = "DS18B20_2" ORDER BY id```  
Click: done  

Doubleclick the set topic node, updating the name and value field to ```sensor2```  
Click: done  

Doubleclick the ```Join sensor payloads``` node incrementing ```After a number of message parts``` to ```2```  
Click: done

Last double click the ```Plot sensor data``` node, in the tab: On Message.  
Add a new input variable ```const input2 = msg.payload.sensor2;```  
In the ```var outObj``` object in ```series``` add a new sensor like so: ```series: ["Sensor1", "Sensor2"],```  
In ```data``` create a new array inside the fist array: ```data: [[],[]],```

Now the ```outObj``` should look like so with two sensors: 
```
var outObj = [{
    series: ["Sensor1", "Sensor2"],
    data: [[],[]],
    lables: [""]
}]
```
Note the two empty arrays in the data field
```
data: [[],[]],
		   ^
		   |
		New array for sensor2
```

<br>  

To add a line, iterate over the new sensor2 input with a for loop, incrementing the number in ```.data``` to add to the second array of the data 3d array
```
for (let item of input2){
    outObj[0].data[1].push({
        x: item.timestamp,
        y: item.reading
    })
}
```
Click: done

Now click Deploy in the top righthand corner and open the dashboard view: ```127.0.0.1:1880/ui/```

---
To recap, with every new sensor make sure to:
- Modify ```main.cpp``` adding two variables and appending them to the payload.
- Modify ```addmqtttemptodb.sh``` add two new variables to store the  output of awk, increment the string, write to DB with sqlite3, inserting the new variables into the command.
- Modify ```flows.json```  add a sensor query, add a topic to the sensor query, join the payloads and update the plot sensor data function.

All done, navigate back to: ```subscriber/```  
Rebuild the main compose file with: ```docker compose -f addmqtttodb_Sub_Broker_compose.yaml up --build```

## Changing IP-addresses, URL and MQTT topics
To do

## To Do
