from flask import request, json, jsonify, Response

from quantum3d.routes import api_bp as app
from quantum3d.db import db, pdb
from quantum3d.constants import GENERAL_SETTINGS_KEYS, MACHINE_SETTINGS_KEYS


@app.route('/settings', methods=['GET', 'POST'])
def general_settings():
    """
    GETs the initial settings

    POSTs the new settings to be set
    """
    if request.method == 'GET':
        general_settings = pdb.get_multiple(GENERAL_SETTINGS_KEYS)
        machine_settings = pdb.get_multiple(MACHINE_SETTINGS_KEYS)
        all_settings = {}
        all_settings.update(general_settings)
        all_settings.update(machine_settings)
        return jsonify(all_settings), 200
    else:
        changed_fields = request.json
        for field in changed_fields:
            pdb.set_key(field, changed_fields[field])
        return Response(status=200)
