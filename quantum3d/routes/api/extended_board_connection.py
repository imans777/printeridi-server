from flask import jsonify, Response

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer


@app.route('/extended_board_connection', methods=['GET'])
def extended_board_connection():
    """
    Returns True if the extended board
    has been connected successfully, else False
    """
    return jsonify({'is_connected': printer.use_ext_board}), 200
