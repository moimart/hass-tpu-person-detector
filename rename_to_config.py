import os
#from dotenv import load_dotenv
# load_dotenv()

device = {
    "identifiers": ["Kikkei Labs Person Detector"],
    "name": "Kikkei's Person Detector",
    "model": "Kikkei-detector-0",
    "manufacturer": "Kikkei Labs",
}

config = {
    "codec": "h264_nvmpi",
    "model": "ssd-mobilenet-v2",
    "threshold": 0.5,
    "source":  "rtsp://1.2.3.4",
    "sources": [
        {
            "name": "Garage",
            "url" : "rtsp://1.2.3.4"
        },
        {
            "name": "Entrance",
            "url": "rtsp://1.2.4.5."
        }
    ],
    "output": "",  # "rtsp://localhost:8554/mystream",
    "hass_username": "homeassistant",
    "hass_pwd": "",
    "mqtt_host": "1.2.3.6",
    "mqtt_port": 1883,
    "mqtt_topic": "homeassistant/binary_sensor/kikkei/jetson_presence/config",
    "mqtt_payload": {
        "availability_topic": "kikkei/occupancy/jetson",
        "state_topic": "kikkei/occupancy/sensor/status",
        "name": "Persons detector",
        "unique_id": "garden_presence",
        "device_class": "occupancy",
        "payload_on": "on",
        "payload_off": "off",
        "payload_available": "ON",
        "payload_not_available": "OFF",
        "device": device
    },
    "mqtt_topic_persons": "homeassistant/sensor/kikkei/jetson_persons/config",
    "mqtt_payload_sensor_persons": {
        "availability_topic": "kikkei/occupancy/jetson",
        "state_topic": "kikkei/occupancy/sensor/persons",
        "name": "Number of Persons",
        "unique_id": "garden_persons",
        "unit_of_measurement": "person",
        "payload_available": "ON",
        "payload_not_available": "OFF",
        "device": device
    },
    "mqtt_topic_last_person_camera": "homeassistant/camera/kikkei/jetson_camera_last_person/config",
    "mqtt_topic_last_person_cameras": "homeassistant/camera/kikkei/jetson_camera_",
    "mqtt_payload_sensor_last_person_camera": {
        "availability_topic": "kikkei/occupancy/jetson",
        "topic": "kikkei/occupancy/sensor/camera_",
        "name": "Last person snapshot",
        "unique_id": "garden_persons_camera",
        "payload_available": "ON",
        "payload_not_available": "OFF",
        "device": device
    },
    "mqtt_topic_cameras_active": "homeassistant/sensor/kikkei/cameras_active/config",
    "mqtt_payload_cameras_active": {
        "availability_topic": "kikkei/occupancy/jetson",
        "state_topic": "kikkei/occupancy/sensor/cameras_active",
        "name": "Cameras Active",
        "unique_id": "garden_presence_cameras_active",
        "payload_on": "on",
        "payload_off": "off",
        "payload_available": "ON",
        "payload_not_available": "OFF",
        "device": device
    }
}
