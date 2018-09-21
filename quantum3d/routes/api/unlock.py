from flask import request, json, Response, jsonify, abort

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer
from quantum3d.db import db


@app.route('/unlock', methods=['POST'])
def unlock():
    """
    Checks if the entered pin code is correct or not
    POST:
        REQUEST: {
            pin: text
        }
    """
    if printer.is_locked:
        if db.get_pin() == request.json['code']:
            printer.is_locked = False
            return Response(status=200)
        else:
            abort(403)
    else:
        abort(404)
