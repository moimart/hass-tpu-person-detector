#!/usr/bin/python3
import jetson.inference
import jetson.utils
from PIL import Image
from config import config, TIME_FORMAT_STR
from time import gmtime, strftime
from timeit import default_timer as timer
from presence_manager import PresenceManager
from custom_timer import Timer
from video_recorder import VideoRecorder
from net_detector import NetDetector
import io
import logging
from multiprocessing import Process
import os

DETECTOR_CLASS = "person"


class MultiVideoDetector:
    def __init__(self):
        logging.basicConfig(filename="kikkei-detector.log",
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

        logging.info("Presence detector log")
        self.logger = logging.getLogger('person-detector')
        self.logger.info("Video detector started")

        self.video_record = False if config["snap_video_duration"] == 0 else True
        self.snap_save = True

        self.sources = []
        for i in config["sources"]:
            input_source = None
            input_source_created = True
            try:
                input_source = jetson.utils.videoSource(i["url"])
            except Exception as e:
                input_source_created = False

            source = {
                "input": input_source,
                "name": i["name"],
                "url": i["url"],
                "active": input_source_created
            }
            self.sources.append(source)
            self.video_recorders[source] = VideoRecorder(
                config["snap_video_duration"])
            self.video_recorders[source].logger = self.logger

        self.pm = PresenceManager()
        self.pm.detector = self

        self.net = NetDetector()

        self.dt = 0
        self.elapsed = 0
        self.processing_gap = config["processing_gap"]

        self.timer_pool = [Timer(120, self) for _ in range(1)]
        for timer in self.timer_pool:
            timer.active = False

    def get_timer(self):
        for timer in self.timer_pool:
            if not timer.active:
                return timer

        return None

    def on_timer(self, timer, elapsed):
        try:
            timer.payload["input"] = jetson.utils.videoSource(
                timer.payload["url"])
        except Exception as e:
            self.logger.error(
                "SOURCE {} COULD NOT BE REACTIVATED".format(timer.payload["name"]))
            return
        timer.payload["active"] = True
        self.logger.info(
            "SOURCE {} WAS REACTIVATED".format(timer.payload["name"]))

    def process_frame(self, name, frame, person_detected):
        image_array = self.net.copy_frame_to_cpu(frame)
        array_frame = Image.fromarray(image_array, "RGB")

        if person_detected:
            with io.BytesIO() as output:
                array_frame.save(output, format="PNG")
                self.pm.last_person_camera(output.getvalue())
                self.pm.update_camera(name, output.getvalue())

            if self.snap_save:
                array_frame.save(
                    "captures/{}-{}.png".format(strftime(TIME_FORMAT_STR, gmtime()), name), "PNG")

    def loop(self):
        self.elapsed += self.dt

        for video_recorder in self.video_recorders.values():
            video_recorder.step(self.dt)

        if self.elapsed < self.processing_gap:
            return
        if self.elapsed >= self.processing_gap*2:
            self.elapsed = 0

        persons_detected = 0
        cameras_active = False

        for source in self.sources:
            cameras_active = cameras_active or source["active"]
            if not source["active"]:
                timer = self.get_timer()
                if timer != None and timer.name != source["name"]:
                    timer.payload = source
                    timer.name = source["name"]
                    timer.reset()
                    timer.active = True
                    self.logger.info(
                        "Trying reactivation of source {}".format(source["name"]))
                continue

            try:
                frame = source["input"].Capture()
            except Exception as e:
                self.logger.error("SOURCE {} FAILED!!!".format(source["name"]))
                source["active"] = False
                continue

            camera_detection = False
            detections = self.net.detect(frame)
            for detection in detections:
                if self.net.get_detection_name(detection) == DETECTOR_CLASS:
                    persons_detected += 1
                    camera_detection = True

            self.process_frame(source["name"], frame, camera_detection)

            if persons_detected > 0 and self.video_record:
                self.video_recorders[source["name"]].start(
                    source["name"], source["url"])

            if not source["input"].IsStreaming():
                source["active"] = False

        self.pm.binary_sensor_status("on" if persons_detected > 0 else "off")
        self.pm.persons_detected(persons_detected)
        self.pm.cameras_active(cameras_active)

        if persons_detected > 0:
            self.pm.last_time_detected("{}".format(
                strftime('%A %B %-d, %I:%M %p', gmtime())))

        if not cameras_active:
            self.logger.error("NO CAMERA SOURCES ARE ACTIVE")

        for timer in self.timer_pool:
            timer.step(self.dt)

    def start(self):
        while True:
            t0 = timer()
            self.loop()
            self.pm.loop()
            t1 = timer()

            self.dt = t1 - t0


if __name__ == "__main__":
    vd = MultiVideoDetector()
    vd.start()
