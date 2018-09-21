from flask import request, jsonify, json, Response

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer


@app.route('/led', methods=['POST'])
def change_led_status():
    """
    Changes the Printer LED on/off status
    POST:
        Request: {
            status: boolean
        }
    """
    status = request.json.get('status')
    if status == 'on':
        printer.set_relay_ext_board(1, True)
    else:
        printer.set_relay_ext_board(1, False)
    return Response(status=200)
