
__author__ = "Iman Sahebi <iman.s_sani@yahoo.com>"
__license__ = "The MIT License <http://opensource.org/licenses/MIT>"
__copyright__ = "Copyright (C) 2018 Iman Sahebi - Released under terms of the MIT License"

from . import queries
from . import pickle_db

# use this db anywhere you want to use database
db = queries.PrinterDB()

# use this pdb anywhere you want to use pickledb
pdb = pickle_db.PickleDB()
