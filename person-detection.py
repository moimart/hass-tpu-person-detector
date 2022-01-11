#!/usr/bin/python3
import ffmpeg
import numpy as np
import jetson.inference
import jetson.utils
from PIL import Image
import paho.mqtt.client as mqtt
import json
from config import config

class PresenceManager:
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        self.client.publish("kikkei/occupancy/jetson","ON")
        self.client.publish(config["mqtt_topic"], json.dumps(config["mqtt_payload"]), retain=True)

    def on_message(self, client, userdata, msg):
        print(msg)
        
    def publish_binary_sensor_status(self, status):
        self.client.publish("kikkei/occupancy/status", status)

    def __init__(self):
        self.client = mqtt.Client()

        self.client.username_pw_set(config["hass_username"], password=config["hass_pwd"])

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(config["mqtt_host"], config["mqtt_port"], 60)

    def loop(self):
        self.client.loop()


class VideoDetector:
    def __init__(self):
        self.pm = PresenceManager()
        self.net = jetson.inference.detectNet(config["model"], threshold=config["threshold"])
        self.input = jetson.utils.videoSource(config["source"])
        self.width = 640
        self.height = 480

        self.ffmpeg_process = (
            ffmpeg.input(
                "pipe:",
                format="rawvideo",
                pix_fmt="rgb24",
                r=15,
                s="{}x{}".format(self.width, self.height),
            )
            # .output("yeah.mp4", pix_fmt='yuv420p')
            .output(config["output"], f="rtsp", pix_fmt="yuv420p", r=15)
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )

    def start(self):
        try:
            self.loop()
        except Exception as e:
            print("Exception {}".format(e))
            self.input = jetson.utils.videoSource(config["source"])

            self.ffmpeg_process.stdin.close()
            self.ffmpeg_process.wait()

            self.ffmpeg_process = (
            ffmpeg.input(
                "pipe:",
                format="rawvideo",
                pix_fmt="rgb24",
                r=15,
                s="{}x{}".format(self.width, self.height),
            )
            # .output("yeah.mp4", pix_fmt='yuv420p')
            .output(config["output"], f="rtsp", pix_fmt="yuv420p", r=15)
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )

    def loop(self):
        prev_detection = False #avoid spamming mqtt server
        while True:
            img = self.input.Capture()
            detections = self.net.Detect(img, overlay="box,labels,conf")

            no_person_detected = True
            for detection in detections:
                if self.net.GetClassDesc(detection.ClassID) == "person":
                    self.pm.publish_binary_sensor_status("on")
                    no_person_detected = False
                    prev_detection = True

            if no_person_detected and prev_detection:
                self.pm.publish_binary_sensor_status("off")
                prev_detection = False

            self.width = img.width
            self.height = img.height

            image_array = jetson.utils.cudaToNumpy(img)
            array_frame = Image.fromarray(image_array, "RGB")

            buffer = array_frame.tobytes()

            self.ffmpeg_process.stdin.write(buffer)
            self.pm.loop()

            if not self.input.IsStreaming():
                break

        self.ffmpeg_process.stdin.close()
        self.ffmpeg_process.wait()


if __name__ == "__main__":
    vd = VideoDetector()
    vd.start()