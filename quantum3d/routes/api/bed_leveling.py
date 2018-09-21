from flask import request, json, Response

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer


@app.route('/bedleveling', methods=['POST'])
def bed_leveling():
    """
    Bed-Levels the device on a certain stage
    POST:
        Request: {
            stage: 1 | 2 | 3 | 4    
        }
    """
    printer.bedleveling_manual(request.json['stage'])
    return Response(status=200)
