
__author__ = "Iman Sahebi <iman.s_sani@yahoo.com>"
__license__ = "The MIT License <http://opensource.org/licenses/MIT>"
__copyright__ = "Copyright (C) 2018 Iman Sahebi - Released under terms of the MIT License"

from .machine import Machine
from .utils import Utils
from .extra import Extra
from .raspberry_hardware_info import RaspberryHardwareInfo

from .print_time import Time
from .extended_board import ExtendedBoard

# import camera driver


def get_camera_list():
    ''' retreive camera list (except rasp pi) '''
    import pygame
    import pygame.camera
    pygame.init()
    pygame.camera.init()
    cams = pygame.camera.list_cameras()
    return cams


import os
from importlib import import_module
from .cameras.camera_pi import Camera as CameraPi
from .cameras.camera_webcam import Camera as CameraWebcam

Camera = {}
Camera['pi'] = CameraPi
Camera['webcam'] = CameraWebcam
selectedCamera = 'pi'


def changeCameraTo(cam):
    # TODO: this doesn't work as expected!
    # maybe a dictionary of cameras' a better idea?
    ''' this changes the Camera object to a desired camera '''
    global Camera
    global selectedCamera
    try:
        if cam == 'pi':
            selectedCamera = 'pi'
        elif 'webcam' in cam:
            Camera['webcam'].selected_camera = int(cam[len('webcam'):])
            selectedCamera = cam
        else:
            return False
    except:
        return False
    return True


# use this objects to work with utility
printer = Machine()
extra = Extra()
print("-> Machine initialized")
