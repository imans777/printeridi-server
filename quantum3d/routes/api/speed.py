from flask import request, json, jsonify, Response, abort

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer


@app.route('/speed', methods=['POST'])
def set_speed():
    """
    Changes the speed of either print or flow by the sent value
    POST:
        Request: {
            field: 'print' || 'flow',
            value: number
        }
    """
    req = request.json
    field = req.get('field', 'print')
    value = req.get('value', 0)
    if field == 'print':
        printer.set_feedrate_speed(value)
    elif field == 'flow':
        printer.set_flow_speed(value)
    else:
        abort(404)
    return Response(status=200)
