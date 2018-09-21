from flask import jsonify

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer


@app.route('/get_time', methods=['GET'])
def get_time():
    """
    Returns the printing time (in seconds)
    GET:
        Response: {
            time: String,
            status: Integer,
        }
    """
    time_read = printer.time.read()
    return jsonify({'time': time_read}), 200
