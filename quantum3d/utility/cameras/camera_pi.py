import io
import time
try:
    import picamera
except ImportError:
    print("Pi Camera not found. Are you running on rpi?")
from .camera_base import CameraBase


class Camera(CameraBase):
    @staticmethod
    def frames():
        try:
            with picamera.PiCamera() as camera:
                # camera initialization
                time.sleep(2)

                stream = io.BytesIO()
                for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                    stream.seek(0)
                    yield stream.read()

                    stream.seek(0)
                    stream.truncate()
        except Exception as e:
            print("pi camera err: ", e)
