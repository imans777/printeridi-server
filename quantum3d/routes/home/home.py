from quantum3d.routes import home_bp as app
from flask import render_template, request
from quantum3d.utility import Utils


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def client_renderer(path):
    client = Utils.get_client_ip(request)
    server = Utils.get_server_ip(request)
    if (client == server):
        return render_template('app.html')
    else:
        # make sure there's no firewall set up!
        return render_template('web.html')
