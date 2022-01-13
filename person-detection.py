#!/usr/bin/python3
import ffmpeg
import numpy as np
import jetson.inference
import jetson.utils
from PIL import Image
import paho.mqtt.client as mqtt
import json
from config import config
from time import gmtime, strftime


class PresenceManager:
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        self.client.publish("kikkei/occupancy/jetson", "ON")
        self.client.publish(config["mqtt_topic"], json.dumps(
            config["mqtt_payload"]), retain=True)

    def on_message(self, client, userdata, msg):
        print(msg)

    def publish_persons_detected(self, persons):
        self.client.publish("kikkei/occupancy/number", persons)

    def publish_binary_sensor_status(self, status):
        self.client.publish("kikkei/occupancy/status", status)

    def __init__(self):
        self.client = mqtt.Client()

        self.client.username_pw_set(
            config["hass_username"], password=config["hass_pwd"])

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(config["mqtt_host"], config["mqtt_port"], 60)

    def loop(self):
        self.client.loop()


class VideoDetector:
    def create_process(self):
        self.ffmpeg_process = (
            ffmpeg.input(
                "pipe:",
                format="rawvideo",
                pix_fmt="rgb24",
                s="{}x{}".format(self.width, self.height),
            )
            .output(config["output"], vcodec="h264_nvmpi", preset="ultrafast", f="rtsp", pix_fmt="yuv420p", r=15)
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )

    def __init__(self):
        self.pm = PresenceManager()
        self.net = jetson.inference.detectNet(
            config["model"], threshold=config["threshold"])
        self.input = jetson.utils.videoSource(config["source"])
        self.width = 320
        self.height = 240
        self.ffmpeg_process = None
        self.video_record = True
        self.snap_save = True

    def start(self):
        try:
            self.loop()
        except Exception as e:
            print("\n\n\n\nRestarting.... Exception {}\n\n\n\n".format(e))
            self.input = jetson.utils.videoSource(config["source"])

            self.ffmpeg_process.stdin.close()
            self.ffmpeg_process.wait()
            self.create_process()

    def process_frame(self, img):
        if self.ffmpeg_process is None:
            self.width, self.height = img.width, img.height
            self.create_process()

        image_array = jetson.utils.cudaToNumpy(img)

        array_frame = Image.fromarray(image_array, "RGB")
        buffer = array_frame.tobytes()

        self.ffmpeg_process.stdin.write(buffer)

        if self.snap_save:
            array_frame.save("{}".format(strftime("%Y%M%d-%H%M%S", gmtime())),"PNG")

    def record_video(self, img, no_person_detected, video_started):
        if self.video_record:
            if not no_person_detected and not video_started:
                self.output = jetson.utils.videoOutput(
                    "{}.mp4".format(strftime("%Y%M%d-%H%M%S", gmtime())))
                self.output.Render(img)
            elif no_person_detected and video_started:
                self.output.Close()
            elif not no_person_detected and video_started:
                self.output.Render(img)

    def loop(self):
        prev_detection = False  # avoid spamming mqtt server
        video_started = False
        while True:
            try:
                img = self.input.Capture()
            except Exception as e:
                raise RuntimeError from e 

            detections = self.net.Detect(img, overlay="box,labels,conf")

            persons_detected = 0
            no_person_detected = True
            for detection in detections:
                if self.net.GetClassDesc(detection.ClassID) == "person":
                    self.pm.publish_binary_sensor_status("on")
                    no_person_detected = False
                    prev_detection = True
                    persons_detected += 1

            self.pm.publish_persons_detected(persons_detected)

            if no_person_detected and prev_detection:
                self.pm.publish_binary_sensor_status("off")
                prev_detection = False

            self.record_video(img, no_person_detected, video_started)
            self.process_frame(img)

            self.pm.loop()

            if not self.input.IsStreaming():
                break

        self.ffmpeg_process.stdin.close()
        self.ffmpeg_process.wait()


if __name__ == "__main__":
    vd = VideoDetector()
    vd.start()
