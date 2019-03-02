from flask import request, json, Response, jsonify, abort

from quantum3d.routes import api_bp as app
from quantum3d.utility import Utils


@app.route('/timelapse', methods=['POST', 'DELETE', 'OPTIONS'])
def timelapse():
    """
    on OPTIONS returns a list of available timelapses
    POSTs a usb name and a directory name to
    export the taken timelapses to that usb
    or
    DELETEs timelapses of a certain directory
    POST:
      Request: {
        usbname: string,
        dirname: string
      }
    DELETE:
      Request: {
        dirname: string
      }
    """
    if request.method == 'OPTIONS':
        tls = Utils.timelapse_list()
        return jsonify({'list': tls}), 200

    dirname = request.json.get('dirname')
    if not dirname:
        abort(403)

    if request.method == 'POST':
        usbname = request.json.get('usbname')
        if not usbname:
            abort(403)

        if Utils.export_timelapse_to_usb(dirname, usbname):
            return Response(status=200)
        abort(404)
    elif request.method == 'DELETE':
        if Utils.remove_timelapse_folder(dirname):
            return Response(status=200)
        abort(404)
