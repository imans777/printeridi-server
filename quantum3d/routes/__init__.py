
__author__ = "Iman Sahebi <iman.s_sani@yahoo.com>"
__license__ = "The MIT License <http://opensource.org/licenses/MIT>"
__copyright__ = "Copyright (C) 2018 Iman Sahebi - Released under terms of the MIT License"

from flask import Blueprint

api_bp = Blueprint('api_bp',
                   __name__)

home_bp = Blueprint('home_bp',
                    __name__,
                    template_folder='templates',
                    static_folder='static')
