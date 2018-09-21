from flask import jsonify

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer


@app.route('/get_z', methods=['GET'])
def get_z():
    """
    Returns the current printer's Z position
    GET:
        Response: {
            z: Integer
        }
    """
    z = printer.get_current_Z_position()
    return jsonify({'z': z}), 200
