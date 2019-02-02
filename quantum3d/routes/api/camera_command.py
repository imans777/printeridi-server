
from flask import request, Response, current_app, abort, json, jsonify
from quantum3d.routes import api_bp as app
from quantum3d.utility import Camera, changeCameraTo
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


@app.route('/camera-list', methods=['GET'])
def cameraList():
    '''
        get list of available cameras
        Response: {
            cameras: {
                name: string,           # the displayed name of the camera
                link: string,           # the link used in changeCameraTo function
                icon: string            # custom icon for different cameras
            }[]
        }
    '''

    # TODO: functionality incomplete!
    return jsonify({
        'cameras': [{
            'name': 'Pi-Camera',
            'link': 'pi',
            'icon': 'camera'
        }, {
            'name': 'Webcam',
            'link': 'webcam',
            'icon': 'photo_camera'
        }]
    })


@app.route('/camera-set', methods=['POST'])
def cameraSet():
    '''
        sets the feeding camera to the requested one
        Request: {
            cam: 'pi' | 'webcam' | ...
        }
    '''
    cam = request.json.get('cam')
    if cam and changeCameraTo(cam):
        return Response(status=200)
    else:
        abort(500)


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
