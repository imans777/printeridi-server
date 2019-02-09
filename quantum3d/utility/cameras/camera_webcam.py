from .camera_base import CameraBase
import pygame
import pygame.camera
import time


class Camera(CameraBase):
    cameraObj = None

    @staticmethod
    def capture(dest, resize=(640, 480)):
        try:
            img = Camera.cameraObj.get_image()
            pygame.image.save(img, dest)
        except Exception as e:
            print("webcam camera capture err: ", e)

    @staticmethod
    def frames():
        try:
            while True:
                pygame.init()
                pygame.camera.init()
                cams = pygame.camera.list_cameras()
                print("camera list : ", cams)
                cam = pygame.camera.Camera(cams[0])

                cam.start()
                Camera.camerObj = cam

                while True:
                    image = cam.get_image()
                    yield image

                cam.stop()
        except Exception as e:
            print("webcam camera frames err: ", e)
            Camera.frames()
