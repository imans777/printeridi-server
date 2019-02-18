import os
from enum import Enum

# base path for usbs
BASE_PATH = os.environ.get('BASE_PATH') or '/media/pi'

# Base upload full path
BASE_FULL_UPLOAD = os.path.join(
    os.getcwd(),
    os.environ['FLASK_APP'] or 'quantum3d',
    os.environ['UPLOAD_FOLDER'] or 'uploads',
)

# screenshots full path
SC_FULL_PATH = os.path.join(BASE_FULL_UPLOAD, 'screenshots')

# upload files fill path (also exists on utility/machine.py)
UPLOAD_FULL_PATH = os.path.join(BASE_FULL_UPLOAD, 'files')

# language folder path
LANGUAGE_FOLDER_FULL_PATH = os.path.join(
    os.getcwd(),
    os.environ['FLASK_APP'] or 'quantum3d',
    os.environ['STATIC_FOLDER'] or 'static',
    'assets',
    'languages'
)

# 'download API' <folder> for usb
USBS = 'usbs'

# valid upload folders
VALID_FOLDERS = [
    'screenshots',
    'files',
    USBS
]

# allowed upload file extensions
ALLOWED_EXTENSIONS = set(
    ['gcode']
)

# upload protocol (also exists on utility/machine.py)
UPLOAD_PROTOCOL = 'upload://'


# supported pickledb keys
PICKLE_KEYS = [
    'lang',
    'theme',
    'print_file_dir',
    'gcode_downloadable_link',
    'sc_index',
    'selected_camera',
    'print_status'
]


class PrintStatus(Enum):
    IDLE = 0        # on print stop
    PRINTING = 1    # other conditions
    PAUSED = 2      # on print pause
