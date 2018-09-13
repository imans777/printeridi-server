from flask import Flask
from quantum3d.routes import home_bp, api_bp
from quantum3d.routes import home, api

printer_app = Flask(__name__)
printer_app.register_blueprint(api_bp, url_prefix='/api')
printer_app.register_blueprint(home_bp)
