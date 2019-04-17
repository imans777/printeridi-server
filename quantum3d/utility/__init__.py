
__author__ = "Iman Sahebi <iman.s_sani@yahoo.com>"
__license__ = "The MIT License <http://opensource.org/licenses/MIT>"
__copyright__ = "Copyright (C) 2018 Iman Sahebi - Released under terms of the MIT License"

from .machine import Machine
from .utils import Utils
from .extra import Extra
from .raspberry_hardware_info import RaspberryHardwareInfo

from .print_time import Time
from .extended_board import ExtendedBoard
from .cameras import Camera, changeCameraTo

# use this objects to work with utility
from quantum3d.db import pdb


def auto_set_default_port():
    default_port = Utils.autofind_printer_serial_port()
    if default_port:
        pdb.set_key('serial_port', default_port)
        print('-> Default Serial Port Found: "{}"'.format(default_port))


auto_set_default_port()

printer = Machine(
    pdb.get_key('serial_port'),
    pdb.get_key('baudrate'),
    pdb.get_key('extruders')
)
extra = Extra()
print("-> Utilities initialized")
