from flask import request, json, jsonify, abort

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer


@app.route('/heat', methods=['POST'])
def heat():
    """
    Heat/Cooldown on a field with the sent value
    POST:
        Request: {
            field: 'hotend' | 'bed',
            action: 'heat' | 'cooldown',
            value: number
        }
        Response: {
            status: 'success' | 'failure'
        }
    """
    data = request.json
    if data['field'] == 'hotend':
        if data['action'] == 'heat':
            printer.set_hotend_temp(data['value'])
        elif data['action'] == 'cooldown':
            printer.cooldown_hotend()
        else:
            abort(403)
    elif data['field'] == 'bed':
        if data['action'] == 'heat':
            printer.set_bed_temp(data['value'])
        elif data['action'] == 'cooldown':
            printer.cooldown_bed()
        else:
            abort(403)
    else:
        abort(403)

    return jsonify({'status': 'success'}), 200
