from flask import request, jsonify

from quantum3d.routes import api_bp as app
from quantum3d.utility import RaspberryHardwareInfo as RHI


@app.route('/hardware-info', methods=['GET'])
def get_hardware_info():
    """
    GETs the current hardware info
    """
    return jsonify({
        'ram_usage': RHI.get_ram_info(),
        'cpu_usage': RHI.get_cpu_use(),
        'cpu_temp': RHI.get_cpu_tempfunc(),
        'gpu_temp': RHI.get_gpu_tempfunc(),
    }), 200
