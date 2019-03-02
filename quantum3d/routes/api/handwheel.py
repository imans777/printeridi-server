from flask import Response, request, jsonify, json

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer


@app.route('/handwheel', methods=['POST', 'PUT'])
def handwheel():
    if request.method == 'POST':
        printer.deactive_handwheel_offset_position()

    if request.method == 'PUT':
        printer.set_handwheel_offset_position()

    return Response(status=200)
