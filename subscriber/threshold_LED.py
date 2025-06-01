import RPi.GPIO as GPIO
import time
import sqlite3 

count = 0
threshold1 = 25
threshold2 = 28
redPin = 17
yellowPin = 27
greenPin = 22

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(redPin, GPIO.OUT)
GPIO.setup(yellowPin, GPIO.OUT)
GPIO.setup(greenPin, GPIO.OUT)

conn = sqlite3.connect("temperature.db")
cursor = conn.cursor()

def getSensor1Latest():
    cursor.execute('SELECT reading FROM temperature1 WHERE sensor_name = "DS18B20_1" ORDER BY rowid desc LIMIT 1')
    sensor1Latest = cursor.fetchall()
    return sensor1Latest

def getSensor2Latest():
    cursor.execute('SELECT reading FROM temperature1 WHERE sensor_name = "DS18B20_2" ORDER BY rowid desc LIMIT 1')
    sensor2Latest = cursor.fetchall()
    return sensor2Latest

def getSensor3Latest():
    cursor.execute('SELECT reading FROM temperature1 WHERE sensor_name = "DS18B20_3" ORDER BY rowid desc LIMIT 1')
    sensor3Latest = cursor.fetchall()
    return sensor3Latest

sensor1LastTemp = getSensor1Latest()
sensor2LastTemp = getSensor2Latest()
sensor3LastTemp = getSensor3Latest()

lastTemp1 = sensor1LastTemp[0][0]
lastTemp2 = sensor2LastTemp[0][0]
lastTemp3 = sensor3LastTemp[0][0]

print ("Latest temps: ")
print (lastTemp1)
print (lastTemp2)
print (lastTemp3)

while count < 3:
    if lastTemp1 < threshold1:
        print ("Sensor1 temp lower than: 24")
        GPIO.output(redPin,True)
        time.sleep(1)
        GPIO.output(redPin,False)
        time.sleep(1)



# state = True

# # endless loop, on/off for 1 second
# while True:
#     GPIO.output(4,True)
#     time.sleep(1)
#     GPIO.output(4,False)
#     time.sleep(1)
