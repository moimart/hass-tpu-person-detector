#!/usr/bin/python3
import ffmpeg
import numpy as np
import jetson.inference
import jetson.utils
from PIL import Image
from config import config
from time import gmtime, strftime
from presence_manager import PresenceManager

class VideoDetector:
    def create_process(self):
        if config["output"] == "":
            return

        f = "rtsp" if config["output"][0:4] == "rtsp" else "mp4"

        self.ffmpeg_encoder = (
            ffmpeg.input(
                "pipe:",
                format="rawvideo",
                pix_fmt="rgb24",
                s="{}x{}".format(self.width, self.height),
            )
            .output(config["output"], vcodec="h264_nvmpi", preset="ultrafast", f=f, pix_fmt="yuv420p", r=15)
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
        self.ffmpeg_encoder = None
        self.video_record = True
        self.snap_save = True

    def start(self):
        try:
            self.loop()
        except Exception as e:
            print("\n\n\n\nRestarting.... Exception {}\n\n\n\n".format(e))
            self.input = jetson.utils.videoSource(config["source"])

            self.ffmpeg_encoder.stdin.close()
            self.ffmpeg_encoder.wait()
            self.create_process()

    def process_frame(self, img, person_detected):        
        if self.ffmpeg_encoder is None and config["output"] != "":
            self.width, self.height = img.width, img.height
            self.create_process()

        image_array = jetson.utils.cudaToNumpy(img)

        array_frame = Image.fromarray(image_array, "RGB")
        buffer = array_frame.tobytes()

        if config["output"] != "":
            self.ffmpeg_encoder.stdin.write(buffer)

        if self.snap_save and person_detected:
            array_frame.save("{}".format(
                strftime("%Y%M%d-%H%M%S", gmtime())), "PNG")

    def record_video(self, img, person_detected, video_started):
        if self.video_record:
            if person_detected and not video_started:
                self.output = jetson.utils.videoOutput(
                    "{}.mp4".format(strftime("%Y%M%d-%H%M%S", gmtime())))
                self.output.Render(img)
            elif not person_detected and video_started:
                self.output.Close()
            elif person_detected and video_started:
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
            person_detected = False
            for detection in detections:
                if self.net.GetClassDesc(detection.ClassID) == "person":
                    self.pm.publish_binary_sensor_status("on")
                    person_detected = True
                    prev_detection = True
                    persons_detected += 1

            self.pm.publish_persons_detected(persons_detected)

            if not person_detected and prev_detection:
                self.pm.publish_binary_sensor_status("off")
                prev_detection = False

            self.record_video(img, person_detected, video_started)
            self.process_frame(img, person_detected)

            self.pm.loop()

            if not self.input.IsStreaming():
                break

        self.ffmpeg_encoder.stdin.close()
        self.ffmpeg_encoder.wait()


if __name__ == "__main__":
    vd = VideoDetector()
    vd.start()
