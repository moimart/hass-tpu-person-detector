import jetson.inference
import jetson.utils
from config import config

class NetDetector:
    def __init__(self):
        self.net = jetson.inference.detectNet(
            config["model"], threshold=config["threshold"])
        
    def detect(self, frame):
        return self.net.Detect(frame, overlay="box,labels,conf")
        
    def copy_frame_to_cpu(self, frame):
        return jetson.utils.cudaToNumpy(frame)

    def get_detection_name(self, detection):
        return self.net.GetClassDesc(detection.ClassID)