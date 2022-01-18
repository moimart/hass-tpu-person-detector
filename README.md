hass-tpu-person-detection
===============

### Python program for person detection for Nvidia's Jetson boards (soon Google's Coral EDGE TPU) integration with HomeAssistant through MQTT

## Features:
* Detects persons in several video streams as a single sensor. Perfect for exterior setups as it is simplified in one detection device
* Creates a device in Home Assistant through MQTT that publishes:
    - Cameras sources are active
    - Last snapshot of detected class (person) per camera
    - Binary Occupancy sensor
    - Number of persons sensor
    - Last time of detection
* Takes snapshots when detection occurs as PNGs with detections
* Takes video files after detection occurs

## TODO:
* Coral EDGE TPU implementation
* Selection of classes to track (not just person)
* Auto-upload of snapshots and videos
* Docker image
* Multiple instances (in order to have multiple Home Assistant's devices)
* Expose labelling data for network training of detections

## Usage:

1. Install dependencies specified in setup.py -- setup.py does not work:

'ffmpeg-python', 'numpy','pillow', 'paho-mqtt' 

If you are using Jetson, you need jetson-inference to be available. Google's Coral EDGE TPU development has not started yet.

```
$ pip3 install ffmpeg-python numpy pillow paho-mqtt
```
3. Rename rename_to_config.py to config.py
4. Edit the config.py to adjust it to your setup
5. Make sure to have a MQTT broker installed with Home Assistant (i.e. Mosquito MQTT Broker)
6. Run the script
```
$ python3 multicamera_detection.py # for multiple cameras (setting sources in config) without rtsp re-stream
```


