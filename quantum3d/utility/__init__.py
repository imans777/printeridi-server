
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
import os
from importlib import import_module
Camera = None
if os.environ.get('CAMERA'):
    Camera = import_module(
        '.cameras.camera_' + os.environ['CAMERA'], package='quantum3d.utility').Camera
else:
    print("!! Camera not found")


def changeCameraTo(cam):
    # TODO: this doesn't work as expected!
    # maybe a dictionary of cameras' a better idea?
    ''' this changes the Camera object to a desired camera '''
    global Camera
    try:
        if cam == 'pi' or cam == 'webcam':
            Camera = import_module('.cameras.camera_' + cam,
                                   package='quantum3d.utility').Camera
        else:  # unsupported camera
            Camera = import_module('.cameras.camera_base',
                                   package='quantum3d.utility').CameraBase
            return False
    except:
        return False
    return True


# use this objects to work with utility
printer = Machine()
extra = Extra()
