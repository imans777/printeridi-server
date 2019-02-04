
import os

# Base upload full path
BASE_FULL_UPLOAD = os.path.join(
    os.getcwd(),
    os.environ['FLASK_APP'] or 'quantum3d',
    os.environ['UPLOAD_FOLDER'] or 'uploads',
)

# screenshots full path
SC_FULL_PATH = os.path.join(BASE_FULL_UPLOAD, 'screenshots')

# upload files fill path
UPLOAD_FULL_PATH = os.path.join(BASE_FULL_UPLOAD, 'files')

# language folder path
LANGUAGE_FOLDER_FULL_PATH = os.path.join(
    os.getcwd(),
    os.environ['FLASK_APP'] or 'quantum3d',
    os.environ['STATIC_FOLDER'] or 'static',
    'assets',
    'languages'
)

# download folder for usb
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

# upload protocol
UPLOAD_PROTOCOL = 'upload://'
