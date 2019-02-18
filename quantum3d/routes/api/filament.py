from flask import Response, jsonify

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer


@app.route('/filament', methods=['GET'])
def filament_changes():
    """
    Checks if the filament has been finished
    and then returns True if it was so
    """
    return jsonify({'filament_flag': printer.is_filament()}), 200
