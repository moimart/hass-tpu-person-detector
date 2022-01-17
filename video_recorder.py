import jetson.utils
from custom_timer import Timer
from config import TIME_FORMAT_STR
from time import gmtime, strftime

class VideoRecorder:
    def __init__(self, duration):
        self.video_is_recording = False
        self.timer = Timer(duration, self)
        self.logger = None

    def start(self, camera, input_source, img):
        if not self.video_is_recording:
            self.timer.reset()
            self.camera = camera
            self.input = input_source
            self.output = jetson.utils.videoOutput(
                "file://captures/{}-{}.mp4".format(strftime(TIME_FORMAT_STR, gmtime()), camera))
            self.output.Render(self.input.Capture())
            self.video_is_recording = True

    def step(self, dt):
        if self.video_is_recording:
            self.output.Render(self.input.Capture())
            self.timer.step(dt)

    def on_timer(self, timer, elapsed):
        self.output.Close()
        self.video_is_recording = False
        if self.logger != None:
            self.logger.info("Video reccording stopped")