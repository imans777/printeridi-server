from flask import request, json, jsonify, Response, abort

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer, extra


@app.route('/move_axis', methods=['OPTIONS', 'POST', 'GET'])
def move_axis():
    """
    GETs the current position of axises
    On OPTIONS, checks if we have the access to move or not
    on POST, it moves if we were authorized to
    OPTIONS:
        Response: {
            access: boolean
        }
    POST:
        Request: {
            axis: 'X' | 'Y' | 'Z' | 'All',
            value: number
        }
    """
    if request.method == 'GET':
        return jsonify({'pos': printer.get_current_position()}), 200

    if request.method == 'OPTIONS':
        return jsonify({'access': extra.checkHomeAxisAccess()}), 200

    if request.method == 'POST':
        if not extra.checkHomeAxisAccess():
            abort(403)

        data = request.json
        printer.move_axis(data['axis'], "Relative", data['value'])
        return Response(status=200)
