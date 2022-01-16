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
        self.client.publish(config["mqtt_topic_cameras_active"], json.dumps(
            config["mqtt_payload_cameras_active"]), retain=True)

        last_camera = config["mqtt_payload_sensor_last_person_camera"].copy()
        last_camera["topic"] = "{}_last_person".format(last_camera["topic"])
        self.client.publish(config["mqtt_topic_last_person_camera"], json.dumps(last_camera), retain=True)

        self.client.publish("kikkei/occupancy/sensor/cameras_active", "on")
        
        self.client.publish("kikkei/occupancy/sensor/persons", 0)

        if self.detector != None:
            for source in self.detector.sources:
                self.register_camera(source["name"])

    def register_camera(self, name):
        camera = config["mqtt_payload_sensor_last_person_camera"].copy()
        camera["name"] = "{} {}".format(camera["name"], name)
        camera["real_name"] = name
        camera["unique_id"] = "{}_{}".format(camera["unique_id"], name.lower())
        camera["topic"] = "{}{}".format(camera["topic"], name.lower())

        camera_topic = "{}{}/config".format(
            config["mqtt_topic_last_person_cameras"], name.lower())

        self.client.publish(camera_topic, json.dumps(
            camera), retain=True)

        self.cameras.append(camera)

    def update_camera(self, camera_name, snap):
        for camera in self.cameras:
            if camera["real_name"] == camera_name:
                self.client.publish(camera["topic"], snap)
                break

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
        self.client.publish("kikkei/occupancy/sensor/camera_last_person", snap)

    def cameras_active(self, active):
        if self.prev_camera_active != active:
            self.client.publish(
                "kikkei/occupancy/sensor/cameras_active", "on" if active else "off")
            self.prev_camera_active = active

    def __init__(self):
        self.client = mqtt.Client()

        self.client.username_pw_set(
            config["hass_username"], password=config["hass_pwd"])

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(config["mqtt_host"], config["mqtt_port"], 60)

        self.prev_persons = 0
        self.prev_status = "off"
        self.prev_camera_active = True

        self.detector = None
        self.cameras = []

    def loop(self):
        self.client.loop()
