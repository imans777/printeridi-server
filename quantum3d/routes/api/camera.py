
from flask import request, Response
from quantum3d.routes import api_bp as app
from quantum3d.utility import Camera


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
      takes an image and saves it locally
    '''
    fr = getLastFrame(Camera())
    import os
    fr.save(os.path.join(os.getcwd(), 'test.jpeg'))
