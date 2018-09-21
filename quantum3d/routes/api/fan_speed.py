from flask import request, json, Response

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer


@app.route('/fan_speed', methods=['POST'])
def fan_speed():
    """
    Sets the fan speed to the desired value
    POST:
        Response: {
            status: 'ON' | 'Half' | 'OFF'
        }
    """
    status = request.json['status']
    printer.fan_status(status)
    return Response(status=200)
