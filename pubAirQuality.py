import os
import fcntl
import time
import paho.mqtt.client as mqtt

I2C_SLAVE = 0x703
PM2008 = 0x28

class PubAirQuality:
    def __init__(self):
        self.mqttc = mqtt.Client()
        self.mqttc.on_connect = self.on_connect
        self.mqttc.connect("localhost")
        self.mqttc.loop_start() 
        
        self.fd = os.open('/dev/i2c-1',os.O_RDWR)
        if self.fd < 0 :
            print("Failed to open the i2c bus\n")
        io = fcntl.ioctl(self.fd,I2C_SLAVE,PM2008)
        if io < 0 :
            print("Failed to acquire bus access/or talk to salve\n")

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to PM2008 with result code %d" % rc)
        
    def getAirQuality(self):
        data = os.read(self.fd, 32)
        pm0p1 = 256 * int(data[13]) + int(data[14])
        pm2p5 = 256 * int(data[15]) + int(data[16])
        pm10 = 256 * int(data[17]) + int(data[18])

        return (pm0p1, pm2p5, pm10)

    def publish(self):
        data = self.getAirQuality()
        strfy = ",".join(map(str, data))
        infot = self.mqttc.publish("sensor/pm2008", strfy)
        infot.wait_for_publish()
        print("Published (%s)" % strfy)
