
__author__ = "Iman Sahebi <iman.s_sani@yahoo.com>"
__license__ = "The MIT License <http://opensource.org/licenses/MIT>"
__copyright__ = "Copyright (C) 2018 Iman Sahebi - Released under terms of the MIT License"

from .machine import Machine
from .utils import Utils
from .extra import Extra
from .raspberry_hardware_info import RaspberryHardwareInfo

from .print_time import Time
from .extended_board import ExtendedBoard

from quantum3d.db import pdb

# import camera driver
import os
from .cameras.camera_pi import Camera as CameraPi
from .cameras.camera_webcam import Camera as CameraWebcam

Camera = {}
Camera['pi'] = CameraPi
Camera['webcam'] = CameraWebcam
pdb.set_key('selected_camera', '')


def changeCameraTo(cam):
    # TODO: this doesn't work as expected!
    # maybe a dictionary of cameras' a better idea?
    ''' this changes the Camera object to a desired camera '''
    global Camera
    try:
        if cam == 'pi':
            pdb.set_key('selected_camera', 'pi')
        elif 'webcam' in cam:
            Camera['webcam'].selected_camera = int(cam[len('webcam'):])
            pdb.set_key('selected_camera', 'webcam')
        else:
            return False
    except:
        return False
    return True


# use this objects to work with utility
serial_port, baudrate = pdb.get_key('serial_port'), pdb.get_key('baudrate')
printer = Machine(serial_port, baudrate)
extra = Extra()
print("-> Machine initialized")
