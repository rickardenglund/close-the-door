#! /usr/bin/python
import RPi.GPIO as GPIO
import time
import soco
from soco import SoCo
from soco.discovery import by_name
from soco.snapshot import Snapshot
import os
import random
 
time.sleep(60)
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 
GPIO_LED =8 
GPIO.setup(GPIO_LED, GPIO.OUT)

zone_list = list(soco.discover())
for zone in zone_list:
    print(zone.player_name)

sound_dir = '/var/www/html/sounds/'
sounds = []
for r, d, f in os.walk(sound_dir):
    for file in f:
        if '.mp3' in file:
            sounds.append(file)

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
def something_there_func(dist):
    default = 182
    return abs(dist - default) > 50


def play():
    file ='http://192.168.1.52/sounds/' + random.choice(sounds)
    try:
        sonos = by_name("Lekrum")
        if sonos.group:
            sonos = sonos.group.coordinator

        snap = Snapshot(sonos)
        snap.snapshot()
        sonos.play_uri(file)
        time.sleep(5)
        snap.restore(fade=True)
    except:
        print("Failed to play on " + str(sonos))


if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            print(dist)
            something_there = something_there_func(dist)
            dist = distance()
            print(dist)
            something_there &= something_there_func(distance())
            play()
            print("close the door")

            if something_there:
                GPIO.output(GPIO_LED, True)
                time.sleep(2)

                time.sleep(1)
            time.sleep(0.4)
            GPIO.output(GPIO_LED, False)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()


