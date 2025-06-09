#!/usr/bin/python3

import os
from subprocess import Popen, PIPE, STDOUT
import threading
import paho.mqtt.client as mqtt
import socket
import json
import time
from rpi_ws281x import PixelStrip, Color
from datetime import datetime, timedelta

class Subscriber:
    def __init__(self):
        self.socCli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socCli.connect(("localhost", 5353))

        self.client =mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("localhost")
        self.client.loop_forever()

    def getCurrentTime(self):
       now = datetime.now() 

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code %s" % rc)
        self.client.subscribe("sensor/dht22")
        self.client.subscribe("sensor/light")
        self.client.subscribe("sensor/pm2008")

    def on_message(self, client, userdata, msg):
        if msg.topic == "sensor/dht22":
            data = msg.payload.decode("utf-8").split(",")
            print("temp : %s, humid : %s" % (data[0], data[1]))
        elif msg.topic == "sensor/light":
            data = msg.payload.decode("utf-8")
            print("light : %s" % data)
            with open("config.json", "r") as f:
                config = json.load(f)
                if int(data) < 50: 
                    now = datetime.now()
                    now = now + timedelta(hours=9)
                    alarmMin = datetime(now.year, now.month, now.day, config["alarmTime"][0], config["alarmTime"][1])
                    alarmMax = alarmMin + timedelta(0, 1800)
                    isAlarmTime = now > alarmMin and now < alarmMax
                    if config["alarmFlag"] and isAlarmTime:
                        self.socCli.send('alarm'.encode())
                        os.system("mpg123 alarm.mp3")
                    if config["moodFlag"] and not isAlarmTime:
                        self.socCli.send('mood'.encode())
                elif int(data) >= 50:
                    self.socCli.send('stop'.encode())
        elif msg.topic == "sensor/pm2008":
            data = msg.payload.decode("utf-8").split(",")
            print("PM0.1 : %s , PM2.5 : %s, PM10 : %s" % (data[0], data[1], data[2]))
    
sub = Subscriber()
