from flask import jsonify

from quantum3d.routes import api_bp as app
from quantum3d.utility import Utils


@app.route('/ip', methods=['POST'])
def ip_list():
    """
    Returns the list of device's IP (if any)
    Also connects to the device to the config-file wifi-settings if provided on second time!
    POST:
        Response: {
            ips: String[]
        }
    """

    if Utils.is_first_time != -1:
        Utils.is_first_time += 1

    if Utils.is_first_time == 2:
        Utils.is_first_time = -1
        Utils.connect_to_config_file_wifi()

    ips = Utils.get_ip_list()
    return jsonify({'ips': ips}), 200
