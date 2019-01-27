
from flask import current_app, send_from_directory, abort
from quantum3d.routes import api_bp as app
from .consts import BASE_FULL_UPLOAD, VALID_FOLDERS
import os

# TODO: the question is how the client should know which 'path' to request?


@app.route('/download/<path:folder>/<path:path>')
def sendFile(folder, path):
    '''
        this api is used for downloading either
          a captured screenshot, or
          an uploaded gcode file,
        given the name
    '''
    if folder not in VALID_FOLDERS:
        abort(404)

    with_folder_path = os.path.join(BASE_FULL_UPLOAD, folder)
    if not os.listdir(with_folder_path):
        abort(404)

    return send_from_directory(os.path.join(with_folder_path), path)
