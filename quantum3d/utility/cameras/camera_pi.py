import io
import time
try:
    import picamera
except ImportError:
    print("Pi Camera not found. Are you running on rpi?")
from .camera_base import CameraBase


class Camera(CameraBase):
    cameraObj = None

    @staticmethod
    def capture(dest, resize=(640, 480)):
        try:
            Camera.cameraObj.capture(dest, resize=resize)
        except Exception as e:
            print("pi camera capture err: ", e)

    @staticmethod
    def frames():
        try:
            with picamera.PiCamera() as camera:
                # camera initialization
                Camera.cameraObj = camera
                time.sleep(2)

                stream = io.BytesIO()
                for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                    stream.seek(0)
                    yield stream.read()

                    stream.seek(0)
                    stream.truncate()
        except Exception as e:
            print("pi camera frames err: ", e)
