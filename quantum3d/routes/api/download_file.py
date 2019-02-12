
from flask import current_app, send_from_directory, abort
from quantum3d.routes import api_bp as app
from quantum3d.constants import BASE_FULL_UPLOAD, VALID_FOLDERS, USBS
import os
from os.path import join

# TODO: the question is how the client should know which 'path' to request?
# (only screenshots left)


@app.route('/download/<path:folder>/<path:path>')
def sendFile(folder, path):
    '''
        this api is used for downloading either
          a captured screenshot, (screenshots)
          or
          an uploaded gcode file, (files)
          or
          a gcode file from usb, (usbs)
        given the name
    '''
    if folder not in VALID_FOLDERS:
        abort(404)

    if folder == USBS:
        # given 'a/b/c/d.gcode':
        #   raw_folder: 'a/b/c' (if sep == '/')
        #   file_name: 'd.gcode'
        raw_folder = join(*str(path).split('/')[:-1])
        file_name = str(path).split('/')[-1]

        with_folder_path = join(
            os.environ['BASE_PATH'] or '/media/pi', raw_folder)
        if not os.listdir(with_folder_path):
            abort(404)

        return send_from_directory(with_folder_path, file_name)
    else:
        with_folder_path = join(BASE_FULL_UPLOAD, folder)
        if not os.listdir(with_folder_path):
            abort(404)

        return send_from_directory(with_folder_path, path)
