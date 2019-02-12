from flask import request, Response, json, jsonify, abort

from quantum3d.routes import api_bp as app
from quantum3d.constants import PICKLE_KEYS
from quantum3d.db import pdb
import os


@app.route('/interaction', methods=['PUT', 'POST'])
def pickleInteraction():
    """
    POSTa key to retreive its value from pickledb
    Request: {
      pkey: string
    },
    Response: {
      pvalue: string | number
    }

    or

    PUTs a key/value to pickledb
    Request: {
      pkey: string,
      pvalue: string | number
    }

    from supported keys
    """
    k, v = request.json.get('pkey'), request.json.get('pvalue')
    if request.method == 'POST':
        if k in PICKLE_KEYS:
            pvalue = pdb.get_key(k)
            return jsonify({'pvalue': pvalue}), 200
    else:
        if k in PICKLE_KEYS:
            pdb.set_key(k, v)
            return Response(status=200)
