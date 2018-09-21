from flask import jsonify

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer


@app.route('/temperatures', methods=['GET'])
def get_temperature():
    """
    Returns the current and goal temperature of bed and extruder
    GET:
        Response: {
            bed: {cur: number, goal: number},
            ext: {cur: number, goal: number}
        }
    """
    printer.refresh_temp()
    bed_temp = printer.get_bed_temp()
    ext_temp = printer.get_extruder_temp()
    data = {
        'bed': {
            'cur': bed_temp['current'],
            'goal': bed_temp['point']
        },
        'ext': {
            'cur': ext_temp['current'],
            'goal': ext_temp['point']
        }
    }
    return jsonify(data), 200
