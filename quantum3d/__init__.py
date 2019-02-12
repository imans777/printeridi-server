
__author__ = "Iman Sahebi <iman.s_sani@yahoo.com>"
__license__ = "The MIT License <http://opensource.org/licenses/MIT>"
__copyright__ = "Copyright (C) 2018 Iman Sahebi - Released under terms of the MIT License"


def env_initiation():
    # Load environment variables
    from dotenv import load_dotenv
    from pathlib import Path  # python3 only
    load_dotenv(verbose=True)
    env_path = Path('..') / '.env'
    load_dotenv(dotenv_path=str(env_path))

    # Necessary fallbacks
    import os
    # check if on raspberry pi platform
    if hasattr(os, 'uname'):
        if os.uname()[4][:3] == 'arm':
            print("Platform Detected: 'raspberry pi'")
            os.environ['CUR_ENV'] = 'rpi'
        else:
            print("Platform Detected: 'linux'")
            os.environ['CUR_ENV'] = os.uanme()[4][:3]
    else:
        print("Platform Detected: 'windows'")
        os.environ['CUR_ENV'] = 'win'

    # check FLASK_APP environ being set
    if os.environ.get('FLASK_APP') is None:
        os.environ['FLASK_APP'] = 'quantum3d'

    # check BASE_PATH to be set
    if os.environ.get('BASE_PATH') is None:
        os.environ['BASE_PATH'] = '/media/pi'

    # check UPLOAD_FOLDER being set
    if os.environ.get('UPLOAD_FOLDER') is None:
        os.environ['UPLOAD_FOLDER'] = 'uploads'

    # check STATIC_FOLDER being set
    if os.environ.get('STATIC_FOLDER') is None:
        os.environ['STATIC_FOLDER'] = 'static'


env_initiation()

# coloring the logs
import logging
LOG_LEVEL = logging.DEBUG
LOGFORMAT = "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
from colorlog import ColoredFormatter
logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOGFORMAT)
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
log = logging.getLogger('pythonConfig')
log.setLevel(LOG_LEVEL)
log.addHandler(stream)


# prepare and create the whole app
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from quantum3d.routes import home_bp, api_bp
from quantum3d.routes import home, api

printer_app = Flask(__name__)
CORS(printer_app)
printer_app.register_blueprint(api_bp, url_prefix='/api')
printer_app.register_blueprint(home_bp)

from quantum3d import db
from quantum3d import utility
from . import constants

from quantum3d import socket_api
socketio = SocketIO(printer_app)
socketio.on_namespace(socket_api.info.SocketBase('/'))


# disable flask logging
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
