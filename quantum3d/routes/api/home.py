from flask import request, json, Response

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer, extra


@app.route('/home', methods=['POST'])
def home_machine():
    """
    Homes the machine on the given axis
    POST:
        Request: {
            axis: 'X' | 'Y' | 'Z' | 'All'
        }
    """
    axis = request.json['axis']
    printer.Home_machine(axis)
    extra.addHomeAxis(axis)
    return Response(status=200)
