#!/usr/bin/python3

import paho.mqtt.client as mqtt
import spidev
import time

class PubLight:
    def __init__(self):
        self.mqttc = mqtt.Client()
        self.mqttc.on_connect = self.on_connect
        self.mqttc.connect("localhost")
        self.mqttc.loop_start()

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 976000
        self.lightChannel = 0

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to Light Sensor with result code %d" % rc)

    def readChannel(self, channel):
        adc = self.spi.xfer2([1, (8 + channel) << 4, 0])
        adcOut = ((adc[1] & 3) << 8) + adc[2]
        
        return adcOut

    def getLightLevel(self):
        lightLevel = self.readChannel(self.lightChannel)
   
        return lightLevel

    def publish(self):
        lightLevel = self.getLightLevel()
        infot = self.mqttc.publish("sensor/light", str(lightLevel))
        infot.wait_for_publish()
        print("Published (%s)" % str(lightLevel))
