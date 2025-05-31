import RPi.GPIO as GPIO
import time
import sqlite3 

con = sqlite3.connect("temperature.db")
cur = con.cursor()

sensor1 = cur.execute("SELECT reading FROM temperature1 WHERE sensor_name = "DS18B20_1" ORDER BY rowid desc LIMIT 1")
print ("Latest sensor1 temp: "+sensor1)

# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(4, GPIO.OUT)

# state = True

# # endless loop, on/off for 1 second
# while True:
#     GPIO.output(4,True)
#     time.sleep(1)
#     GPIO.output(4,False)
#     time.sleep(1)
