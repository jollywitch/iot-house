#!/usr/bin/python3

import paho.mqtt.client as mqtt
import Adafruit_DHT as dht
import time

class PubTempHumid:
    def __init__(self):
        self.mqttc = mqtt.Client()
        self.mqttc.on_connect = self.on_connect
        self.mqttc.connect("localhost")
        self.mqttc.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to DHT22 with result code %d" % rc)

    def getTempHumid(self):
        humid, temp = dht.read_retry(dht.DHT22, 13)
        return (temp, humid)

    def publish(self):
        temp, humid = self.getTempHumid()
        strfy = ",".join(map(str, (round(temp, 2), round(humid, 2))))
        infot = self.mqttc.publish("sensor/dht22", strfy)
        infot.wait_for_publish()
        print("Published (%s)" % strfy)
