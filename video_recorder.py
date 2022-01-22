import jetson.utils
from custom_timer import Timer
from config import TIME_FORMAT_STR
from time import gmtime, strftime
from timeit import default_timer as timer
from multiprocessing import Process
import ffmpeg

class VideoRecorder:
    def __init__(self, duration):
        self.video_is_recording = False
        self.timer = Timer(duration, self)
        self.duration = duration
        self.logger = None
        self.p = None

    def start(self, camera, input_url):
        if not self.video_is_recording:
            output = "captures/{}-{}.mp4".format(strftime(TIME_FORMAT_STR, gmtime()), camera)
            self.video_is_recording = True
            self.timer.reset()
            self.p = (
                    ffmpeg.input(
                        input_url,
                        rtsp_transport="tcp")
                    .output(output, vcodec="h264_nvmpi", preset="ultrafast", t=self.duration, pix_fmt="yuv420p")
                    .overwrite_output()
                    .run_async()
            )
            self.logger.info("Video recording started")
        else:
            self.logger.info("Another video is being recorded")

    def step(self, dt):
        self.timer.step(dt)

    def on_timer(self, timer, elapsed):
        self.video_is_recording = False
        if self.logger != None:
            self.logger.info("Video reccording stopped. Timer stopped at {}".format(elapsed))
        
        #self.p.wait()
