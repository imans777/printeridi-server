import os
from flask import request, Response, abort, current_app, send_from_directory, jsonify
from werkzeug.utils import secure_filename

from quantum3d.routes import api_bp as app
from quantum3d.db import db
from .consts import ALLOWED_EXTENSIONS, UPLOAD_FULL_PATH


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload-file', methods=['POST'])
def uploadFile():
    """
    POST the uploaded gcode file(s) and
    add them to the database
    """
    # NOTE: this 'uploadFile' key is the same in client
    if 'uploadFile' not in request.files:
        abort(404)
    file = request.files['uploadFile']
    if not file.filename:
        abort(404)

    if file and allowed_file(file.filename):
        if not os.path.isdir(UPLOAD_FULL_PATH):
            os.makedirs(UPLOAD_FULL_PATH)
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FULL_PATH, filename))
    return Response(status=200)


# TODO: need an API for printer settings
# TODO: need an API for getting raspberry hardware info

@app.route('/upload-file', methods=['GET'])
def getUploadedFiles():
    """
    GETs the name of all the uploaded files
    """
    if not os.path.isdir(UPLOAD_FULL_PATH):
        os.makedirs(UPLOAD_FULL_PATH)
    files = os.listdir(UPLOAD_FULL_PATH)
    filenames = []
    for name in files:
        if os.path.isfile(os.path.join(UPLOAD_FULL_PATH, name)) and str(name).endswith('.gcode'):
            filenames.append(str(name))
    return jsonify({'files': filenames})


@app.route('/upload-file/<path:path>', methods=['DELETE'])
def deleteFile(path):
    """
    DELETEs an uploaded file given the name (e.g. 'test.gcode')
    """
    # upload directory must exist
    if not os.path.isdir(UPLOAD_FULL_PATH):
        abort(404)

    # there should not be os separator to be used for directories
    if os.path.sep in path or '/' in path or '\\' in path:
        abort(404)

    # file should exist and should be of file type
    full_file_path = os.path.join(UPLOAD_FULL_PATH, path)
    if not os.path.isfile(full_file_path):
        abort(404)

    os.remove(full_file_path)
    return Response(status=200)
