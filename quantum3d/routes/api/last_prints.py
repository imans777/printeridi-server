from flask import request, json, jsonify, Response

from quantum3d.routes import api_bp as app
from quantum3d.db import db


@app.route('/last_prints', methods=['GET'])
def get_last_prints_info():
    """
    Returns the info of the last n prints
    (n = limit is passed in request)
    GET:
        Request: {
            limit: number
        }
        Response: [{print info}]
    """
    limit = request.json.get('limit') or 10
    data = db.get_last_prints(limit)
    return jsonify(data), 200
