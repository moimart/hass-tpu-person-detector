from config import config
from time import gmtime, strftime
import paho.mqtt.client as mqtt
import json


class PresenceManager:
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        self.client.publish("kikkei/occupancy/jetson", "ON")
        self.client.publish(config["mqtt_topic"], json.dumps(
            config["mqtt_payload"]), retain=True)
        self.client.publish(config["mqtt_topic_persons"], json.dumps(
            config["mqtt_payload_sensor_persons"]), retain=True)
        self.client.publish(config["mqtt_topic_last_person_camera"], json.dumps(
            config["mqtt_payload_sensor_last_person_camera"]), retain=True)

    def on_message(self, client, userdata, msg):
        pass

    def publish_persons_detected(self, persons):
        if self.prev_persons != persons:
            self.client.publish("kikkei/occupancy/sensor/persons", persons)
            self.prev_persons = persons

    def publish_binary_sensor_status(self, status):
        if self.prev_status != status:
            self.client.publish("kikkei/occupancy/sensor/status", status)
            self.prev_status = status

    def publish_last_person_camera(self, snap):
        self.client.publish("kikkei/occupancy/sensor/last_person_camera",snap)

    def __init__(self):
        self.client = mqtt.Client()

        self.client.username_pw_set(
            config["hass_username"], password=config["hass_pwd"])

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(config["mqtt_host"], config["mqtt_port"], 60)

        self.prev_persons = 0
        self.prev_status = "off"

    def loop(self):
        self.client.loop()
