from flask import jsonify

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer


@app.route('/on_print_page', methods=['POST'])
def is_on_print_page():
    """
    Returns 'print' if there's already a printing going on, else 'other'
    POST:
        Response: {
            page: 'print' || 'other'
        }
    """
    if printer.on_the_print_page:
        return jsonify({'page': 'print'}), 200
    else:
        return jsonify({'page': 'other'}), 200
