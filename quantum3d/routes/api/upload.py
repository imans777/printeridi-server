import os
from flask import request, Response, abort, current_app
from werkzeug.utils import secure_filename

from quantum3d.routes import api_bp as app
from quantum3d.db import db

ALLOWED_EXTENSIONS = set(
    ['gcode']
)


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
    if file.filename == '':
        abort(404)

    if file and allowed_file(file.filename):
        upload_folder = os.path.join(
            os.getcwd(),
            os.environ['FLASK_APP'] or 'quantum3d',
            current_app.config['UPLOAD_FOLDER']
        )

        if not os.path.isdir(upload_folder):
            os.mkdir(upload_folder)
        filename = secure_filename(file.filename)
        file.save(os.path.join(upload_folder, filename))
    return Response(status=200)


# temp apis here for camera feeds
from quantum3d.utility import Camera


def generateCameraFeed(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/camera-feed')
def cameraFeed():
    '''
        receives feed from the selected camera
    '''
    return Response(generateCameraFeed(Camera()),
                    mimetype='multipart/x-mixed/replace; boundary=frame')
