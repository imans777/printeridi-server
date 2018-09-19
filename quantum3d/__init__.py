from flask import Flask
from flask_socketio import SocketIO
from quantum3d.routes import home_bp, api_bp
from quantum3d.routes import home, api

printer_app = Flask(__name__)
printer_app.register_blueprint(api_bp, url_prefix='/api')
printer_app.register_blueprint(home_bp)

from quantum3d import db
from quantum3d import utility

from quantum3d import socket_api
socketio = SocketIO(printer_app)
socketio.on_namespace(socket_api.info.SocketBase('/'))


def db_initiation():
    # initialize database tables and default settings
    dbObj = db.db
    dbObj.create_settings_table()
    default_settings = dbObj.get_settings()
    dbObj.set_settings(default_settings)
    dbObj.create_last_prints_table()
    print('-> database initialized successfully')


db_initiation()
