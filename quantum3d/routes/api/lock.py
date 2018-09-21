from flask import Response

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer
from quantum3d.db import db


@app.route('/lock', methods=['POST'])
def lock():
    """
    Locks the device if a pin is already set
    """
    pin = db.get_pin()
    if pin is None:
        return Response(status=404)
    else:
        printer.is_locked = True
        return Response(status=200)
