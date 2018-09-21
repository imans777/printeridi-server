from flask import request, json, jsonify, Response

from quantum3d.routes import api_bp as app
from quantum3d.db import db


@app.route('/abs', methods=['GET', 'POST'])
def ask_before_starting():
    """
    GET or SET the ABS value in database
    ABS value is abreviation of Ask Before Status
    if set to 0 (False), the printer wouldn't ask the user
    to continue if there was an existing print going on and
    continues from the previous hibernated print.

    POST:
        Request: {
            abs: boolean
        }

    GET:
        Response: {
            abs: boolean
        }
    """
    if request.method == 'POST':
        db.set_abs(int(request.json['abs']))
        return Response(status=200)
    elif request.method == 'GET':
        return jsonify({'abs': bool(db.get_abs() == 1)}), 200
