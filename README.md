hass-jetson-person-detection
===============

# Python script for person detection for Nvidia's Jetson boards

## Features:
* Publishes ffmpeg rtsp stream (RTSP server needed -- check rtsp-simple-server)
* Creates Home Assistant occupancy sensor with mqtt

## Usage:

1. Install dependencies
```
$ python3 setup.py
```

2. Setup an rtsp server such as rtsp-simple-server from https://github.com/aler9/rtsp-simple-server
3. Rename rename_to_config.py to config.py
4. Edit the config.py to adjust it to your setup
5. Make sure to have a MQTT broker installed with Home Assistant (i.e. Mosquito MQTT Broker)
6. Run the script
```
$ python3 person-detection.py
```

