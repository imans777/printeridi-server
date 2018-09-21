from flask import request, json, jsonify

from quantum3d.routes import api_bp as app
from quantum3d.utility import Utils


@app.route('/wifi', methods=['OPTIONS', 'POST'])
def wifi():
    """
    Returns a list of available wifis on OPTIONS
    Connects to a wifi on POST
    OPTIONS:
        Response: {
            list: String[]
        }
    POST:
        Request: {
            ssid: String,
            password: String
        }
        Response: {
            status: 'success' | 'failure'
        }
    """
    if request.method == 'OPTIONS':
        return jsonify({'list': Utils.wifi_list()}), 200
    elif request.method == 'POST':
        un = request.json['ssid']
        pw = request.json['password']
        ans = Utils.wifi_con(un, pw)
        if ans == 'success':
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'status': 'failure'})
