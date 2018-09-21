from flask import request, json, jsonify, Response
from os.path import isfile

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer, Utils


@app.route('/directory', methods=['POST'])
def dir_list():
    """
    Changes current directory of the printer
    POST:
        Request: {
            cd: String
        }
        Response: {
            data: String[],
            type: 'dir' | 'file',
            status: 'success' | 'failure'
        }
    """
    req = request.json
    file_addr = req['cd']
    if file_addr.endswith('.gcode') and isfile(printer.base_path + '/' + file_addr):
        return jsonify({
            'status': 'success',
            'data': file_addr,
            'type': 'file'
        }), 200
    data = Utils.get_connected_usb(
    ) if req['cd'] == '' else Utils.get_usb_files(req['cd'])
    return jsonify({
        'status': 'success',
        'data': data,
        'type': 'dir'
    }), 200
