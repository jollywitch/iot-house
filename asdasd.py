#!/usr/bin/python3

import os
from subprocess import Popen, PIPE, STDOUT
import threading
import paho.mqtt.client as mqtt
import json
import time
from rpi_ws281x import PixelStrip, Color
from datetime import datetime, timedelta

class NeoPixelThr(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(NeoPixelThr, self).__init__(*args, **kwargs)    
    
        LED_COUNT = 64        # Number of LED pixels.
        LED_PIN = 21          # GPIO pin connected to the pixels (18 uses PWM!).
        LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
        LED_DMA = 10          # DMA channel to use for generating signal (try 10)
        LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
        LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
        LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

        self.stopEvent = threading.Event()

        self.strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.strip.begin()

        self.stopEvent = threading.Event()

    def stop(self):
        self.stopEvent.set()

    # Define functions which animate LEDs in various ways.
    def colorWipe(self, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms / 1000.0)


    def theaterChase(self, color, wait_ms=50, iterations=10):
        """Movie theater light style chaser animation."""
        for j in range(iterations):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, color)
                self.strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, 0)


    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)


    def rainbow(self, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256 * iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel((i + j) & 255))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)


    def rainbowCycle(self, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256 * iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel(
                    (int(i * 256 / self.strip.numPixels()) + j) & 255))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)


    def theaterChaseRainbow(self, wait_ms=50):
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, self.wheel((i + j) % 255))
                self.strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, 0)

    def run(self, param):
        try:
            if param == "alarm":
                self.theaterChase(Color(127, 127, 127))
            elif param == "mood":
                self.rainbow()
            #self.colorWipe(Color(255, 0, 0))  # Red wipe
            #self.colorWipe(Color(0, 255, 0))  # Green wipe
            #self.colorWipe(Color(0, 0, 255))  # Blue wipe
            #self.theaterChase(Color(127, 127, 127))  # White theater chase
            #self.theaterChase(Color(127, 0, 0))  # Red theater chase
            #self.theaterChase(Color(0, 0, 127))  # Blue theater chase
            #self.rainbow()
            #self.rainbowCycle()
            #self.theaterChaseRainbow()
        finally:
            self.colorWipe(Color(0, 0, 0), 10)

class Subscriber:
    def __init__(self):
        self.neoPixelThr = NeoPixelThr()
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
                            if not self.neoPixelThr.is_alive():
                                os.system("mpg321 alarm.mp3")
                                self.neoPixelThr.run("alarm")
                    if config["moodFlag"] and not isAlarmTime:
                        if not self.neoPixelThr.is_alive():
                            self.neoPixelThr.run("mood")
                elif int(data) >= 50:
                    if self.neoPixelThr.is_alive():
                        self.neoPixelThr.stop()
        elif msg.topic == "sensor/pm2008":
            data = msg.payload.decode("utf-8").split(",")
            print("PM0.1 : %s , PM2.5 : %s, PM10 : %s" % (data[0], data[1], data[2]))
    
sub = Subscriber()
