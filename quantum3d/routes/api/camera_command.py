
from flask import request, Response, current_app, abort, json, jsonify
from quantum3d.routes import api_bp as app
from quantum3d.utility import Camera, changeCameraTo
from quantum3d.db import pdb
from .consts import SC_FULL_PATH
import os
import subprocess
import pygame
import pygame.camera


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
    pygame.camera.init()
    webcamlist = pygame.camera.list_cameras()

    vc_out = subprocess.Popen(
        ['vcgencmd', 'get_camera'], stdout=subprocess.PIPE).communicate()[0]
    print("vc out is : ", vc_out)
    
    return jsonify({
        'cameras': [{
            'name': 'Pi-Camera',
            'link': 'pi',
            'icon': '/static/assets/rpicamera.png',
        }, {
            'name': 'Webcam',
            'link': 'webcam',
            'icon': '/static/assets/webcam.png'
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
    webcam_list = pygame.camera.list_cameras()
    cam = request.json.get('cam')
    if cam and changeCameraTo(cam):
        return Response(status=200)
    else:
        abort(500)


@app.route('/camera-save', methods=['POST'])
def cameraSaveImage():
    '''
      takes (captures) an image and saves it locally
    '''
    if not os.path.isdir(SC_FULL_PATH):
        os.makedirs(SC_FULL_PATH)

    f, idx = pdb.get_key('print_file_dir'), pdb.get_key('sc_index')

    f = f.split('.')[0].split('/')[-1]
    pdb.set_key('sc_index', idx + 1)

    Camera().capture(os.path.join(
        SC_FULL_PATH,
        f + str(idx) + '.jpeg'
    ))
    return Response(status=200)
