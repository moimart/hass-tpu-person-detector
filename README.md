hass-jetson-person-detection
===============

# Python script for person detection for Nvidia's Jetson boards

## Features:
* Detects persons in a video stream
* Publishes ffmpeg rtsp stream with detections (RTSP server needed -- check rtsp-simple-server)
* Creates Home Assistant occupancy sensor with mqtt based on detection

## Usage:

1. Install dependencies specified in setup.py -- setup.py does not work:

'ffmpeg-python', 'numpy','pillow', 'paho-mqtt'
```
$ pip3 install ffmpeg-python numpy pillow paho-mqtt
```
2. Setup an rtsp server such as rtsp-simple-server from https://github.com/aler9/rtsp-simple-server
3. Rename rename_to_config.py to config.py
4. Edit the config.py to adjust it to your setup
5. Make sure to have a MQTT broker installed with Home Assistant (i.e. Mosquito MQTT Broker)
6. Run the script(s)
```
$ python3 person_detection.py # for a single camera with rtsp re-stream if output is defined
```
or
```
$ python3 multicamera_detection.py # for multiple cameras (setting sources in config) without rtsp re-stream
```

