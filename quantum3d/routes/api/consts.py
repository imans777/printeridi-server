
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


# valid upload folders
VALID_FOLDERS = [
    'screenshots',
    'files'
]

# allowed upload file extensions
ALLOWED_EXTENSIONS = set(
    ['gcode']
)
