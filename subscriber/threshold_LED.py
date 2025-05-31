import RPi.GPIO as GPIO
import time
import sqlite3 

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)

state = True

# endless loop, on/off for 1 second
while True:
    GPIO.output(4,True)
    time.sleep(1)
    GPIO.output(4,False)
    time.sleep(1)
