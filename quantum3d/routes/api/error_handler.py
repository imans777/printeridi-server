from quantum3d.routes import api_bp as app
from werkzeug.exceptions import HTTPException
from flask import Response, jsonify


@app.errorhandler(403)
def error_not_authorized(e):
    print('ERROR (403 - Not Authorized) -> ', e)
    return Response(status=403)


@app.errorhandler(404)
def error_not_found(e):
    print('ERROR (404 - Not Found) -> ', e)
    return Response(status=404)


@app.errorhandler(500)
def error_internal_server(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    print('ERROR (500 - Internal Server) -> ', e)
    return jsonify(error=str(e)), code


@app.errorhandler(Exception)
def error_handler(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    print('ERROR (from code) -> ', e)
    return jsonify(error=str(e)), code
