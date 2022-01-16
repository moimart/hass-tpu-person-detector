#!/usr/bin/python3
import ffmpeg
import numpy as np
import jetson.inference
import jetson.utils
from PIL import Image
from config import config
from time import gmtime, strftime
from presence_manager import PresenceManager
import io


class MultiVideoDetector:

    def __init__(self):
        self.pm = PresenceManager()
        self.net = jetson.inference.detectNet(
            config["model"], threshold=config["threshold"])
        self.video_record = False
        self.snap_save = True

        self.sources = []
        for i in config["sources"]:
            source = {
                "input" : jetson.utils.videoSource(i),
                "name" : i,
                "active" : True
            }
            self.sources.append(source)

    def start(self):
        try:
            self.loop()
        except Exception as e:
            print("\n\n\n\nRestarting.... Exception {}\n\n\n\n".format(e))
            self.input = jetson.utils.videoSource(config["source"])

            self.ffmpeg_encoder.stdin.close()
            self.ffmpeg_encoder.wait()

    def process_frame(self, img, person_detected):
        
        image_array = jetson.utils.cudaToNumpy(img)

        array_frame = Image.fromarray(image_array, "RGB")
        buffer = array_frame.tobytes()

        if person_detected:
            with io.BytesIO() as output:
                array_frame.save(output, format="PNG")
                self.pm.publish_last_person_camera(output.getvalue())

            if self.snap_save:
                array_frame.save("captures/{}".format(
                    strftime("%Y%M%d-%H%M%S.png", gmtime())), "PNG")

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

    def stop_record_video(self):
        self.output.Close()

    def loop(self):
        skip_frame = 0
        while True:
            skip_frame = skip_frame + 1
            if skip_frame == 15:
                skip_frame = 0
                continue

            persons_detected = 0
            person_detected = False

            for source in self.sources:
                if not source["active"]:
                    continue 
                img = source["input"].Capture()
                detections = self.net.Detect(img, overlay="box,labels,conf")
                for detection in detections:
                    if self.net.GetClassDesc(detection.ClassID) == "person":
                        person_detected = True
                        prev_detection = True
                        persons_detected += 1

                self.process_frame(source.name, img, person_detected)

                if not source["input"].isStreaming():
                    source["active"] = False

            self.pm.publish_binary_sensor_status("on" if person_detected else "off")
            self.pm.publish_persons_detected(persons_detected)
            
            self.pm.loop()

if __name__ == "__main__":
    vd = MultiVideoDetector()
    vd.loop()
