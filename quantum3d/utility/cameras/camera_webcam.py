from .camera_base import CameraBase
import pygame
import pygame.camera
from pygame.locals import *
import time


class Camera(CameraBase):
    cameraObj = None
    selected_camera = '/dev/video0'

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
                cam = pygame.camera.Camera(cams[Camera.selected_camera or 0])
                cam.start()
                Camera.camerObj = cam

                while True:
                    image = cam.get_image()
                    yield image

                cam.stop()
        except Exception as e:
            print("webcam camera frames err: ", e)
