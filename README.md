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

Three files must be modified to add sensors to the system.
- ```main.cpp```
- ```addmqtttemptodb.sh```
- ```st_active_temperature_graph.py```

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
### Adding sensors: st_active_temperature_graph.py
From the subscriber folder open: ```st_active_temperature_graph.py```

In the ```updateGraph()``` function, add a variable to store the sql query: ```temperature1_sensor2 = conn.query('SELECT * FROM temperature1 WHERE sensor_name = "DS18B20_2" ORDER BY id')```  
Replacing the sensor_name in the query with the same name defined in the ```main.cpp``` program.

Create a pandas dataframe with the queried data: ```temperature1_sensor2_df = pd.DataFrame(temperature1_sensor2)```

Append the new dataframe to the function return: ```return temperature1_sensor1_df, temperature1_sensor2_df```

With two sensors the ```updateGraph()``` function would look like this:
```
def updateGraph():
	conn = st.connection('temperature_db', type='sql')
	
	#Add sensor query here
	temperature1_sensor1 = conn.query('SELECT * FROM temperature1 WHERE sensor_name = "DS18B20_1" ORDER BY id')
	temperature1_sensor2 = conn.query('SELECT * FROM temperature1 WHERE sensor_name = "DS18B20_2" ORDER BY id')
	
	temperature1_sensor1_df = pd.DataFrame(temperature1_sensor1)
	temperature1_sensor2_df = pd.DataFrame(temperature1_sensor2)
	
	return temperature1_sensor1_df, temperature1_sensor2_df
```
<br>

In the __while true__ loop find the line: ```sensor1_df, sensor2_df = updateGraph()``` and a new variable sepereated by comma.

So if you have two sensor's returned from ```updateGraph()``` be sure to have two variables when calling the function.
```
return temperature1_sensor1_df, temperature1_sensor2_df
                    |               |
                    |               |
                  sensor1_df, sensor2_df = updateGraph()
```
<br>

Within ```with placeholder.container():```  
Draw a new line with:
```
line2 = (
			alt.Chart(sensor2_df)
			.mark_line()
			.encode(x="timestamp", y="reading")
		)
```
Replacing the variable in ```alt.Chart```, with the name of the variable from ```updateGraph()```  
The strings in ```.encode``` are names of column's in the temperature1 table in the DB

Draw the new line with ```st.altair_chart(line1+line2)```

With two lines drawn it looks like so:
```
sensor1_df, sensor2_df = updateGraph()
	
	with placeholder.container():
		line1 = (
			alt.Chart(sensor1_df)
			.mark_line()
			.encode(x="timestamp", y="reading", color=alt.value("red"))
		)
		line2 = (
			alt.Chart(sensor2_df)
			.mark_line()
			.encode(x="timestamp", y="reading")
		)
		
		st.altair_chart(line1+line2)
```
Save the file

---
To recap, with every new sensor make sure to:
- Modify ```main.cpp``` adding two variables and appending them to the payload.
- Modify ```addmqtttemptodb.sh``` add two new variables to store the  output of awk, increment the string, write to DB with sqlite3, inserting the new variables into the command.
- Modify ```st_active_temperature_graph.py``` Query from the DB into a variable, create a pandas dataframe from query, return the dataframe. Call updategraph() with new variable to store new dataframe, draw new line with new df. 

All done, navigate back to: ```subscriber/```  
Rebuild the main compose file with: ```docker compose -f addmqtttodb_Sub_Broker_compose.yaml up --build```

## Changing IP-addresses, URL and MQTT topics
To do

## To Do
Add: Streamlit dashboard service to compose file which reads DB.   __DONE!!!__  
Add: Two more temperature sensors which writes to db __PARTIAL! (Added one sensor)__  
Add: Two new sensors to streamlit dashboard __PARTIAL! (Added one)__