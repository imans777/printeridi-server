
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
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    print("!! Camera not found")

# use this objects to work with utility
printer = Machine()
extra = Extra()
