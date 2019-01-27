
from flask import request, Response
from quantum3d.routes import api_bp as app
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
                    mimetype='multipart/x-mixed-replace; boundary=frame')
