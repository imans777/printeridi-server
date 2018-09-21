from flask import request, json, Response

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer


@app.route('/extrude', methods=['POST'])
def extrude():
    """
    Extrudes on a certain value and feedrate
    POST:
        Request: {
            value: number,
            feedrate: number (Optional)
        }
    """
    data = request.json
    if 'feedrate' in data:
        printer.extrude(data['value'], data['feedrate'])
    else:
        printer.extrude(data['value'])
    return Response(status=200)
