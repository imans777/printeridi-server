import os
from quantum3d.db import pdb
from quantum3d.constants import SC_FULL_PATH
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


def captureImage():
    ''' capture image automatically '''
    try:
        full_file_name = pdb.get_key('print_file_dir')
        trim_file_name = str(full_file_name).split('.')[0].split('/')[-1]
        final_folder = os.path.join(SC_FULL_PATH, trim_file_name)

        if not os.path.isdir(final_folder):
            os.makedirs(final_folder)

        index = pdb.get_key('sc_index')
        pdb.set_key('sc_index', int(index) + 1)

        cam = pdb.get_key('selected_camera')
        Camera[cam]().capture(os.path.join(
            final_folder,
            str(index) + '.jpeg'
        ))
        return True
    except Exception as e:
        print("error capturing image: ", e)
        return False
