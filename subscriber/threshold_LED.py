import RPi.GPIO as GPIO
import time
import sqlite3 
from RPLCD.i2c import CharLCD

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

def writeLED():
    lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=20, rows=4, dotsize=8)
    #lcd.clear()
    lcd.write_string('Sensor1: ')
    lcd.write_string(lastTemp1String)
    
    lcd.cursor_pos = (1,0)
    lcd.write_string('Sensor2: ')
    lcd.write_string(lastTemp2String)
    
    lcd.cursor_pos = (2,0)
    lcd.write_string('Sensor3: ')
    lcd.write_string(lastTemp3String)

print ("Latest temps: ")
while count < 3:
    sensor1LastTemp = getSensor1Latest()
    sensor2LastTemp = getSensor2Latest()
    sensor3LastTemp = getSensor3Latest()

    lastTemp1 = sensor1LastTemp[0][0]
    lastTemp2 = sensor2LastTemp[0][0]
    lastTemp3 = sensor3LastTemp[0][0]
    
    lastTemp1String = str(lastTemp1)
    lastTemp2String = str(lastTemp2)
    lastTemp3String = str(lastTemp3)
    
    writeLED()
    
    print (lastTemp1)
    print (lastTemp2)
    print (lastTemp3)
    
    # ~ GPIO.output(redPin,True)
    # ~ GPIO.output(yellowPin,True)
    # ~ GPIO.output(greenPin,True)
    # ~ time.sleep(1)
    # ~ GPIO.output(redPin,False)
    # ~ GPIO.output(yellowPin,False)
    # ~ GPIO.output(greenPin,False)
    # ~ time.sleep(1)
    # ~ count += 1
    # ~ print (count)
    
    #Green LED
    if lastTemp1 < threshold1 and lastTemp2 < threshold1 and lastTemp3 < threshold1:
        print ("All below 25C")
        GPIO.output(greenPin,True)
        GPIO.output(redPin,False)
        GPIO.output(yellowPin,False)
    
    #Yellow LED
    if lastTemp1 > threshold1 or lastTemp2 > threshold1 or lastTemp3 > threshold1:
        print ("Above 25C")
        GPIO.output(yellowPin,True)
        GPIO.output(redPin,False)
        GPIO.output(greenPin,False)
        
    #Red LED
    if lastTemp1 > threshold2 or lastTemp2 > threshold2 or lastTemp3 > threshold2:
        print ("Above 28C")
        GPIO.output(redPin,True)
        GPIO.output(yellowPin,False)
        GPIO.output(greenPin,False)

# state = True

# # endless loop, on/off for 1 second
# while True:
#     GPIO.output(4,True)
#     time.sleep(1)
#     GPIO.output(4,False)
#     time.sleep(1)
