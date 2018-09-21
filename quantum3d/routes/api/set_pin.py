from flask import request, json, Response

from quantum3d.routes import api_bp as app
from quantum3d.db import db


@app.route('/set_pin', methods=['PUT'])
def set_pin():
    """
    Sets the child-lock pin-code to the sent code
    PUT:
        Request: {
            code: number (4 digit, preferably)
        }
    """
    db.set_pin(request.json['code'])
    return Response(status=200)
