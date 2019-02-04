from flask import request, json, jsonify, Response
from os.path import isfile, join
from quantum3d.routes import api_bp as app
from quantum3d.utility import printer, Utils


@app.route('/directory', methods=['POST'])
def dir_list():
    """
    Changes current directory of the printer
    and gets folders and gcode files inside.
    POST:
        Request: {
            cd: String (usb1/folder1/file1.gcode)
        }
        Response: {
            data: String[],
            type: 'dir' | 'file',
            status: 'success' | 'failure'
        }
    """
    req = request.json
    file_addr = req['cd']
    if file_addr.endswith('.gcode') and isfile(join(printer.base_path, file_addr)):
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
