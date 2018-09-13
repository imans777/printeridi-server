from quantum3d.routes import home_bp
from flask import render_template


@home_bp.route('/', defaults={'path': ''})
@home_bp.route('/<path:path>')
def client_renderer(path):
    # TODO: should separate client views
    return render_template('app.html')
