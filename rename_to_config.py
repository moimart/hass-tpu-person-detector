import os
#from dotenv import load_dotenv
#load_dotenv()

config = {
    "model": "ssd-mobilenet-v2",
    "threshold": 0.5,
    "source": "rtsp://1.2.3.4:8554/mystream",
    "output": "rtsp://localhost:8554/mystream",
    "hass_username": "homeassistant",
    "hass_pwd": "******",
    "mqtt_host": os.environ.get("MQTT_HOST"),
    "mqtt_port" : os.environ.get("MQTT_PORT"),
    "mqtt_topic": "homeassistant/binary_sensor/kikkei/jetson_presence/config",
    "mqtt_payload": {
        "availability_topic": "kikkei/occupancy/jetson",
        "state_topic": "kikkei/occupancy/status",
        "name": "Garage Presence Detection",
        "unique_id": "garden_presence",
        "device_class": "occupancy",
        "payload_on": "on",
        "payload_off": "off",
        "payload_available": "ON",
        "payload_not_available": "OFF",
        "device": {
            "identifiers": ["Kikkei Labs Jetson Presence Detector"],
            "name": "Kikkei Jetson Presence",
            "model": "Kikkei-Jetson-0",
            "manufacturer": "Kikkei Labs",
        }
    }
}