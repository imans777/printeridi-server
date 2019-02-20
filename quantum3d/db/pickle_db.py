
__author__ = "Iman Sahebi <iman.s_sani@yahoo.com>"
__license__ = "The MIT License <http://opensource.org/licenses/MIT>"
__copyright__ = "Copyright (C) 2019 Iman Sahebi - Released under terms of the MIT License"

import pickledb
import os
from .error_handler import error_handler_with, pickle_message
from quantum3d.constants import PrintStatus, PICKLE_KEYS


class PickleDB:
    def __init__(self):
        try:
            self.db = pickledb.load(os.path.join(
                os.path.dirname(__file__),
                'printerpickle.db'
            ), True)
            print("-> pickledb initialized")
            self._initiate()

        except Exception as e:
            print("could not create pickledb connection: ", e)
            self.db = None

    def _initiate(self):
        self._init_values([
            ('view3d', False),
            ('rotate', True),
            ('filament', False),
            ('lcd', False),
            ('width', 20),
            ('height', 20),
            ('extruders', 1),
            ('serial_port', '/dev/ttyUSB0'),
            ('baudrate', 250000),

            ('bedleveling_X1', 50),
            ('bedleveling_X2', 180),
            ('bedleveling_Y1', 50),
            ('bedleveling_Y2', 180),
            ('traveling_feedrate', 3000),
            ('bedleveling_Z_offset', 10),
            ('bedleveling_Z_move_feedrate', 1500),
            ('hibernate_Z_offset', 5),
            ('hibernate_Z_move_feedrate', 1500),
            ('pause_Z_offset', 10),
            ('pause_Z_move_feedrate', 1500),
            ('printing_buffer', 15),
            ('X_pause_position', 0),
            ('Y_pause_position', 0),
            ('X_timelapse_position', 0),
            ('Y_timelapse_position', 0),
        ], False)
        self._init_values([
            ('sc_index', 0),
            ('print_status', PrintStatus.IDLE.value)
        ], True)

    def _init_values(self, values, force=False):
        for item in values:
            if force or not self.db.exists(item[0]):
                self.set_key(item[0], item[1])

    @error_handler_with(pickle_message)
    def get_key(self, key):
        if key not in PICKLE_KEYS:
            raise "KEY '{}' NOT KNOWN!".format(key)

        # if key doesn't exists, returns 'False'
        return self.db.get(key)

    @error_handler_with(pickle_message)
    def get_multiple(self, keys):
        result = {}
        for key in keys:
            result[key] = self.get_key(key)
        return result

    @error_handler_with(pickle_message)
    def set_key(self, key, value):
        if key not in PICKLE_KEYS:
            raise "KEY '{}' NOT KNOWN!".format(key)

        return self.db.set(key, value)
