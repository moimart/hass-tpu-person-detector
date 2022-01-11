#!/usr/bin/python3
import paho.mqtt.client as mqtt
from config import config

config = {
    "hass_username": "homeassistant",
    "hass_pwd": "oochoh9yeithaech6iequai8iiW9ah8aXeu5sieWoh6ohC7Ahxiet7ahghaiCai3",
    "mqtt_host": "10.20.30.80",
    "mqtt_port" : 1883
}

class mqtt_tester:
    def __init__(self):
        self.client = mqtt.Client()

        self.client.username_pw_set(config["hass_username"], password=config["hass_pwd"])

        self.client.on_connect = self.on_connect
        self.client.connect(config["mqtt_host"], config["mqtt_port"], 60)
    
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
    
    def turn(self,status):
        self.client.publish("kikkei/occupancy/status", status)

if __name__ == "__main__":
    tester = mqtt_tester()
    tester.turn("off")
