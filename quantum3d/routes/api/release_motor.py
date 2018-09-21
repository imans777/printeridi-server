from flask import Response

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer


@app.route('/release_motor', methods=['POST'])
def release_motor():
    printer.release_motors()
    return Response(status=200)
