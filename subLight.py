import paho.mqtt.client as mqtt

class SubLight:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("localhost")

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to Light Sensor with result code %s" % str(rc))
        self.client.subscribe("sensor/light")

    def on_message(self, client, userdata, msg):
        print("Topic : %s\nMessage : %s" % (msg.topic, msg.payload.decode("utf-8")))

    def start(self):
        self.client.loop_forever()

    def stop(self):
        self.client.unsubscribe("sensor/light")
        self.client.disconnect()
