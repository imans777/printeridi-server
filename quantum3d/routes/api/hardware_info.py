import os
from flask import request, jsonify, abort

from quantum3d.routes import api_bp as app
from quantum3d.utility import RaspberryHardwareInfo as RHI


@app.route('/hardware-info', methods=['GET'])
def get_hardware_info():
    """
    GETs the current hardware info
    """
    if os.environ.get('CUR_ENV') != 'rpi':
        abort(403)

    return jsonify({
        'ram_usage': RHI.get_ram_info(),
        'cpu_usage': RHI.get_cpu_use(),
        'cpu_temp': RHI.get_cpu_tempfunc(),
        'gpu_temp': RHI.get_gpu_tempfunc(),
    }), 200
