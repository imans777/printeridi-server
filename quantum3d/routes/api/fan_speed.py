from flask import request, json, Response, jsonify

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer


@app.route('/fan_speed', methods=['GET', 'POST'])
def fan_speed():
    """
    GETs the current fan status

    Sets the fan speed to the desired value
    POST:
        Response: {
            status: 'ON' | 'Half' | 'OFF'
        }
    """
    if request.method == 'GET':
        fan = printer.speed['fan']
        return jsonify({'fan': fan}), 200
    else:
        status = request.json['status']
        printer.fan_status(status)
        return Response(status=200)
