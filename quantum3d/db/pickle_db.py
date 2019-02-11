

__author__ = "Iman Sahebi <iman.s_sani@yahoo.com>"
__license__ = "The MIT License <http://opensource.org/licenses/MIT>"
__copyright__ = "Copyright (C) 2019 Iman Sahebi - Released under terms of the MIT License"

import pickledb
import os
from .error_handler import error_handler_with, pickle_message


class PickleDB:
    def __init__(self):
        try:
            self.db = pickledb.load(os.path.join(
                os.path.dirname(__file__),
                'printerpickle.db'
            ), False)
            print("-> pickledb initialized")
            self._init_values()
        except Exception as e:
            print("could not create pickledb connection: ", e)
            self.db = None

    def _init_values(self):
        self.set_key('sc_index', 0)
        self.set_key('is_paused', 0)

    @error_handler_with(pickle_message)
    def get_key(self, key):
        return self.db.get(key)

    @error_handler_with(pickle_message)
    def set_key(self, key, value):
        cond1 = self.db.set(key, value)
        cond2 = self.db.dump()
        return cond1 and cond2
