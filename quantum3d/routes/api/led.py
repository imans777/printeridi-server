from quantum3d.routes import api_bp as app
from flask import request, jsonify, json, Response


@app.route('/led', methods=['POST'])
def change_led_status():
    status = request.json.get('status')
    if status == 'on':
        pass
        # TODO: printer must be implemented
        # printer.set_relay_ext_board(1, True)
    else:
        pass
        # printer.set_relay_ext_board(1, False)
    return Response(status=200)
