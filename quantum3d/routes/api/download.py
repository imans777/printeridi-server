
from flask import current_app, send_from_directory, abort
from quantum3d.routes import api_bp as app
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
    print('folder :', folder)
    if folder not in ['screenshots', 'files']:
        abort(404)

    return send_from_directory(os.path.join(
        os.getcwd(),
        os.environ['FLASK_APP'],
        current_app.config['UPLOAD_FOLDER'],
        folder
    ), path)
