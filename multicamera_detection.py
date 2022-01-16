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
        self.video_record = False
        self.snap_save = True

        self.sources = []
        for i in config["sources"]:
            source = {
                "input" : jetson.utils.videoSource(i["url"]),
                "name" : i["name"],
                "active" : True
            }
            self.sources.append(source)

        self.pm = PresenceManager()
        self.pm.detector = self

        self.net = jetson.inference.detectNet(
            config["model"], threshold=config["threshold"])

    def process_frame(self, name, img, person_detected):
        
        image_array = jetson.utils.cudaToNumpy(img)
        array_frame = Image.fromarray(image_array, "RGB")

        if person_detected:
            with io.BytesIO() as output:
                array_frame.save(output, format="PNG")
                self.pm.publish_last_person_camera(output.getvalue())
                self.pm.update_camera(name,output.getvalue())

            if self.snap_save:
                array_frame.save("captures/{}-{}.png".format(
                    strftime("%Y%M%d-%H%M%S", gmtime()),name), "PNG")

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

            cameras_active = False
            for source in self.sources:
                cameras_active = cameras_active or source["active"]
                if not source["active"]:
                    continue 

                try:
                    img = source["input"].Capture()
                except Exception as e:
                    print("Source failed!!!")
                    source["active"] = False
                    continue
                
                detections = self.net.Detect(img, overlay="box,labels,conf")
                for detection in detections:
                    if self.net.GetClassDesc(detection.ClassID) == "person":
                        persons_detected += 1

                self.process_frame(source["name"], img, persons_detected > 0)

                if not source["input"].IsStreaming():
                    source["active"] = False

            self.pm.publish_binary_sensor_status("on" if persons_detected > 0 else "off")
            self.pm.publish_persons_detected(persons_detected)
            self.pm.cameras_active(cameras_active)
            
            if not cameras_active:
                print("\n\nCAMERAS ARE NOT ACTIVE!!!\n\n")

            self.pm.loop()

if __name__ == "__main__":
    vd = MultiVideoDetector()
    vd.loop()
