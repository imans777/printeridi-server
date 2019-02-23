from quantum3d.db import pdb
from .camera_pi import Camera as CameraPi
from .camera_webcam import Camera as CameraWebcam

Camera = {
    'pi': CameraPi,
    'webcam': CameraWebcam
}


def changeCameraTo(cam):
    # TODO: this doesn't work as expected!
    # maybe a dictionary of cameras' a better idea? -> NOR IT WORKS!
    ''' this changes the Camera object to a desired camera '''
    global Camera
    try:
        if cam == 'pi':
            pdb.set_key('selected_camera', 'pi')
        elif 'webcam' in cam:
            Camera['webcam'].selected_camera = int(cam[len('webcam'):])
            pdb.set_key('selected_camera', 'webcam')
        else:
            return False
    except:
        return False
    return True
