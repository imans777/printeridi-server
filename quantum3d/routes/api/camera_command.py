
from flask import request, Response, current_app, abort
from quantum3d.routes import api_bp as app
from quantum3d.utility import Camera
from .consts import SC_FULL_PATH
import os


def getLastFrame(camera):
    return camera.get_frame()


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
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# TODO: maybe an API is needed to get which camera you want to use
# and then update Camera variable in utility/__init__ so it be dynamic


@app.route('/camera-save')
def cameraSaveImage():
    '''
      takes (captures) an image and saves it locally
    '''
    if not os.path.isdir(SC_FULL_PATH):
        os.makedirs(SC_FULL_PATH)
    Camera().capture(os.path.join(
        SC_FULL_PATH,
        # TODO: this should be a name according to the model's filename and the z-layer (maybe +timestamp?)
        'test.jpeg'
    ))
    return Response(status=200)
