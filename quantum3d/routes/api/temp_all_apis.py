# from flask import Flask, request, render_template, url_for, Response, json, jsonify
# from utils import Machine, Utils, Extra
# from os.path import isfile
# import subprocess
# import time

# import logging
# LOG_LEVEL = logging.DEBUG
# LOGFORMAT = "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
# from colorlog import ColoredFormatter
# logging.root.setLevel(LOG_LEVEL)
# formatter = ColoredFormatter(LOGFORMAT)
# stream = logging.StreamHandler()
# stream.setLevel(LOG_LEVEL)
# stream.setFormatter(formatter)
# log = logging.getLogger('pythonConfig')
# log.setLevel(LOG_LEVEL)
# log.addHandler(stream)

# app = Flask(__name__)
# printer = Machine()
# extra = Extra()

# ''' disable flask logging '''
# import logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

# @app.route('/api/extended_board_connection', methods=['GET'])
# def extended_board_connection():
#     try:
#         return jsonify({'is_connected': printer.use_ext_board}), 200
#     except Exception as e:
#         log.error('Error in getting extended board connection: %s' % e)
#         # print('Error in getting extended board connection: ', e)
#         return Response(status=500)


# @app.route('/api/filament', methods=['GET'])
# def filament_changes():
#     try:
#         printer.update_filament_status()
#         return jsonify({'filament_flag': printer.is_filament()}), 200
#     except Exception as e:
#         log.error('Error in getting filament flag: %s' % e)
#         return Response(status=500)


# @app.route('/api/speed', methods=['POST'])
# def set_speed():
#     try:
#         req = request.json
#         field = req.get('field', 'print')  # DEFAULTS TO BE SET
#         value = req.get('value', 0)  # DEFAULTS TO BE SET
#         if field == 'print':
#             # printer.set_travel_speed(value)
#             printer.set_feedrate_speed(value)
#         elif field == 'flow':
#             printer.set_flow_speed(value)
#             # printer.set_feedrate_speed(value)
#         else:
#             return Response(status=404)
#         return Response(status=200)

#     except Exception as e:
#         log.error('Error in setting the speed: %s' % e)
#         # print('Error in setting the speed:', e)
#         return Response(status=500)


# @app.route('/api/last_prints', methods=['GET'])
# def recent_print_status():
#     try:
#         data = printer.get_recent_print_status()
#         return jsonify(data), 200
#     except Exception as e:
#         log.error('Error in getting last print: %s' % e)
#         # print('Error in getting :', e)
#         return Response(status=500)


# @app.route('/api/abs', methods=['GET', 'POST'])
# def ask_before_starting():
#     """
#     POST:
#         Request:
#         {
#             abs: boolean
#         }
#         Response:
#         {
#         }

#     GET:
#         Response:
#         {
#             abs: boolean
#         }
#     """
#     if request.method == 'POST':
#         try:
#             status = request.json['abs']
#             # print(status)
#             status_string = "yes" if status == True else "no"
#             printer.set_abs(status_string)
#             return Response(status=200)
#         except Exception as e:
#             log.error('Error in setting abs: %s' % e)
#             # print('Error in getting abs:', e)
#             return Response(status=500)
#     elif request.method == 'GET':
#         try:
#             ask_before_boolean = True if printer.get_abs() == "yes" else False
#             return jsonify({'abs': ask_before_boolean}), 200
#         except Exception as e:
#             log.error('Error in getting abs: %s' % e)
#             # print('Error in getting abs:', e)
#             return Response(status=500)


# @app.route('/api/get_z', methods=['GET'])
# def get_z():
#     """
#     Response:
#     {
#         z: Integer
#     }
#     """
#     try:
#         z = printer.get_current_Z_position()
#         return jsonify({'z': z}), 200
#     except Exception as e:
#         log.error('error in getting Z: %s' % e)
#         # print('error in getting Z:', e)
#         return Response(status=500)

# # TODO: TEMP API -> on the print page


# @app.route('/api/on_print_page', methods=['POST'])
# def on_print_page():
#     """
#     POST:
#     {

#     }
#     """
#     if request.method == 'POST':
#         try:
#             # LOG ON THE PRINT PAGE
#             print('on the print page: ', printer.on_the_print_page)
#             if printer.on_the_print_page:
#                 return jsonify({'page': 'print'}), 200
#             else:
#                 return jsonify({'page': 'other'}), 200
#         except Exception as e:
#             # print('error in printing page:', e)

#             log.error('error in printing page: %s' % e)
#             return Response(status=500)


# @app.route('/api/set_pin', methods=['PUT'])
# def set_pin():
#     try:
#         pin = request.json['code']
#         print(pin)
#         print(printer.set_pin(pin))
#         return Response(status=200)
#     except Exception as e:
#         log.error('Error in setting pin: %s' % e)
#         # print('Error in setting pin: ', e)
#         return Response(status=500)


# @app.route('/api/unlock', methods=['POST'])
# def unlock():
#     """
#     POST:
#         REQUEST:
#         {
#             pin: var char
#         }

#         RESPONSE:
#         {
#             status: Integer
#         }
#     """
#     try:
#         if printer.is_locked:
#             pin = printer.fetch_pin()
#             if pin == int(request.json['code']):
#                 printer.is_locked = False
#                 return Response(status=200)
#             else:
#                 return Response(status=403)
#         else:
#             return Response(status=404)
#     except Exception as e:
#         log.error('error in unlocking the device: %s' % e)
#         # print('error in unlocking the device:', e)
#         return Response(status=500)  # RETURN STATUS CODE TO BE RE-DEFINED


# @app.route('/api/lock', methods=['POST'])
# def lock():
#     """
#     POST:
#     {
#     }
#     """
#     try:
#         pin = printer.fetch_pin()
#         if pin is None:
#             return Response(status=404)
#         else:
#             printer.is_locked = True
#             return Response(status=200)
#         # else:
#         #     return Response(status=503) # RETURN STATUS CODE TO BE RE-DEFINED
#     except Exception as e:
#         log.error('Error in locking the device: %s' % e)
#         # print('Error in locking the device:', e)
#         return Response(status=500)  # RETURN STATUS CODE TO BE RE-DEFINED


# @app.route('/api/get_time', methods=['GET'])
# def get_time():
#     """
#     GET:
#     {
#         time: String,
#         status: Integer,
#     }
#     """
#     try:
#         time_read = printer.time.read()
#         return jsonify({'time': time_read}), 200
#     except Exception as e:
#         log.error('Error in getting the time: %s' % e)
#         # print('Error in getting the time:', e)
#         return Response(status=500)


# @app.route('/api/temperatures', methods=['GET'])
# def temperatures():
#     # TODO: DECORATORS WORK BETTER HERE! ALI EDIT: WAIT FOR ME TO THINK MORE ABOUT IT.
#     # mw = middleWare(request)
#     # if mw[0]:
#         # return jsonify(mw[1])
#     """
#     GET:
#     {
#         bed: {cur: Number, goal: Number},
#         ext: {cur: Number, goal: Number}
#     }
#     """
#     if request.method == 'GET':
#         try:
#             printer.refresh_temp()
#             bed_temp = printer.get_bed_temp()
#             ext_temp = printer.get_extruder_temp()
#             data = {
#                 'bed': {
#                     'cur': bed_temp['current'],
#                     'goal': bed_temp['point']
#                 },
#                 'ext': {
#                     'cur': ext_temp['current'],
#                     'goal': ext_temp['point']
#                 }
#             }
#             return jsonify(data), 200
#         except Exception as e:
#             log.error('error in getting temps: %s' % e)
#             # print('error in getting temps: ', e)
#             return Response(status=500)


# @app.route('/api/wifi', methods=['OPTIONS', 'POST'])
# def wifi():
#     """
#     OPTIONS:
#     {
#         list: String[]
#     }

#     POST:
#     {
#         ssid: String,
#         password: String
#     }
#     {
#         status: 'success' | 'failure'
#     }
#     """
#     try:
#         if request.method == 'OPTIONS':
#             return jsonify({'list': Utils.wifi_list()}), 200
#         elif request.method == 'POST':
#             un = request.json['ssid']
#             pw = request.json['password']
#             ans = Utils.wifi_con(un, pw)
#             if ans == 'success':
#                 return jsonify({'status': 'success'}), 200
#             else:
#                 return jsonify({'status': 'failure'})
#     except Exception as e:
#         log.error('error in wifi: %s' % e)
#         # print('error in wifi:', e)
#         return Response(status=500)


# @app.route('/api/move_axis', methods=['OPTIONS', 'POST'])
# def move_axis():
#     """
#     OPTIONS:
#     {
#         access: Boolean (it needs homing first!)
#     }

#     POST:
#     {
#         axis: 'X' | 'Y' | 'Z' | 'All',
#         value: Number
#     }
#     """
#     if request.method == 'OPTIONS':
#         try:
#             if extra.checkHomeAxisAccess():
#                 return jsonify({'access': True}), 200
#             else:
#                 return jsonify({'access': False}), 200
#         except Exception as e:
#             log.error('error in gaining access for moving %s' % e)
#             # print('error in gaining access for moving', e)
#             return Response(status=500)
#     if request.method == 'POST':
#         try:
#             if extra.checkHomeAxisAccess() is False:
#                 raise

#             data = request.json
#             printer.move_axis(data['axis'], "Relative", data['value'])
#             return Response(status=200)
#         except Exception as e:
#             log.error('ERROR in moving axis: %s' % e)
#             # print("ERROR in moving axis:", e)
#             return jsonify({'access': False}), 500


# @app.route('/api/home', methods=['POST'])
# def home_machine():
#     """
#     POST:
#     {
#         axis: 'X' | 'Y' | 'Z' | 'All'
#     }
#     """
#     if request.method == 'POST':
#         try:
#             axis = request.json['axis']
#             printer.Home_machine(axis)
#             extra.addHomeAxis(axis)
#             return Response(status=200)
#         except Exception as e:
#             log.error('ERROR in homing: %s' % e)
#             # print("ERROR in homing:", e)
#             return Response(status=500)


# @app.route('/api/release_motor', methods=['POST'])
# def release_motor():
#     if request.method == 'POST':
#         try:
#             printer.release_motors()
#             return Response(status=200)
#         except Exception as e:
#             log.error('ERROR in releasing motor: %s' % e)
#             # print("ERROR in releasing motor:", e)
#             return Response(status=500)


# @app.route('/api/directory', methods=['POST'])
# def usb_list():
#     """
#     POST:
#     {
#         cd: String
#     }
#     {
#         data: String[],
#         type: 'dir' | 'file',
#         status: 'success' | 'failure'
#     }
#     """
#     if request.method == 'POST':
#         try:
#             req = request.json
#             file_addr = req['cd']
#             if file_addr.endswith('.gcode') and isfile(printer.base_path + '/' + file_addr):
#                 return jsonify({'status': 'success', 'data': file_addr, 'type': 'file'}), 200
#             print('it wasn\'t file!')
#             data = Utils.get_connected_usb(
#             ) if req['cd'] == '' else Utils.get_usb_files(req['cd'])
#             print('the files:', data)
#             return jsonify({'status': 'success', 'data': data, 'type': 'dir'}), 200
#         except Exception as e:
#             log.error('error in setting directory: %s' % e)
#             # print("error in setting directory:", e)
#             return Response(status=500)


# @app.route('/api/fan_speed', methods=['POST'])
# def fan_speed():
#     """
#     POST:
#     {
#         status: 'ON' | 'Half' | 'OFF'
#     }
#     """
#     if request.method == 'POST':
#         try:
#             status = request.json['status']
#             printer.fan_status(status)
#             return Response(status=200)
#         except Exception as e:
#             log.error('ERROR in setting fan speed: %s' % e)
#             # print("ERROR in setting fan speed: ", e)
#             return Response(status=500)


# @app.route('/api/heat', methods=['POST'])
# def heat():
#     """
#     POST
#     {
#         field: 'hotend' | 'bed',
#         action: 'heat' | 'cooldown',
#         value: Number
#     }
#     {
#         status: 'success' | 'failure'
#     }
#     """
#     try:
#         data = request.json
#         if data['field'] == 'hotend':
#             if data['action'] == 'heat':
#                 printer.set_hotend_temp(data['value'])
#             elif data['action'] == 'cooldown':
#                 printer.cooldown_hotend()
#             else:
#                 raise
#         elif data['field'] == 'bed':
#             if data['action'] == 'heat':
#                 printer.set_bed_temp(data['value'])
#             elif data['action'] == 'cooldown':
#                 printer.cooldown_bed()
#             else:
#                 raise
#         else:
#             raise

#         return jsonify({'status': 'success'}), 200
#     except Exception as e:
#         log.error('Error in heating: %s' % e)
#         # print("Error in heating:", e)
#         return jsonify({'status': 'failure'}), 500


# @app.route('/api/extrude', methods=['POST'])
# def extrude():
#     """
#     POST:
#     {
#         value: Number,
#         feedrate: Number (Optional)
#     }
#     """
#     if request.method == 'POST':
#         try:
#             data = request.json
#             if 'feedrate' in data:
#                 printer.extrude(data['value'], data['feedrate'])
#             else:
#                 printer.extrude(data['value'])
#             return Response(status=200)
#         except Exception as e:
#             log.error('ERROR in extruding: %s' % e)
#             # print("ERROR in extruding:", e)
#             return Response(status=500)


# @app.route('/api/bedleveling', methods=['POST'])
# def bed_leveling():
#     """
#     POST:
#     {
#         stage: 1 | 2 | 3 | 4    
#     }
#     """
#     if request.method == 'POST':
#         try:
#             stage = request.json['stage']
#             printer.bedleveling_manual(stage)
#             return Response(status=200)
#         except Exception as e:
#             log.error('ERROR in bedleveling: %s' % e)
#             # print("ERROR in bedleveling: ", e)
#             return Response(status=500)


# @app.route('/api/print', methods=['DELETE', 'POST'])
# def print_it():
#     """
#     POST:
#     {
#         action: 'print' | 'stop' | 'pause' | 'resume' | 'percentage' | 'unfinished'
#         cd: String, (only if it was print)
#         line: Number (Optional)
#     }

#     default response:
#     {
#         status: 'success' | 'failure'
#         percentage: Number
#     }
#     unfinished response:
#     {
#         status: 'success' | 'failure'
#         unfinished: {
#             exist: True | False,
#             (if exist:)
#             cd: String,
#             line: Number
#         }
#     }

#     DELETE:
#     {}{}

#     """
#     if request.method == 'POST':
#         try:
#             req = request.json
#             action = req['action']
#             # status = {'status': 'success', 'status_code': 200}
#             percentage = 0

#             if action == 'print':
#                 ''' refresh the  ext board buffer to able get the filament error ''' 
#                 # printer.ext_board_flush_input_buffer()
#                 # printer.ext_board_off_A_flag()
#                 ''' delete last printed back up files '''
#                 printer.delete_last_print_files()
#                 # try:
#                 gcode_file_address = req['cd']
#                 if printer.base_path in gcode_file_address:
#                     gcode_file_address = gcode_file_address[len(
#                         printer.base_path)+1:]
#                 if 'line' in req:
#                     printer.start_printing_thread(
#                         gcode_dir=gcode_file_address, line=req['line'])
#                 else:
#                     printer.start_printing_thread(gcode_dir=gcode_file_address)
#                 # except Exception as e:
#                 #     print('ERROR:', e)
#                 #     status = {'status': str(e), 'status_code': 500}
#             elif action == 'stop':
#                 printer.stop_printing()
#                 printer.delete_last_print_files()
#                 ''' wait until the buffer been free '''
#                 time.sleep(1)
#                 printer.release_motors()
#                 printer.cooldown_hotend()
#                 printer.cooldown_bed()
#                 printer.stop_move_up()
#             elif action == 'resume':
#                 printer.resume_printing()
#             elif action == 'pause':
#                 printer.pause_printing()
#             elif action == 'percentage':
#                 percentage = printer.get_percentage()
#             elif action == 'unfinished':
#                 cfup = printer.check_for_unfinished_print()
#                 if cfup[0] == True:
#                     return jsonify({
#                         'status': 'success',
#                         'unfinished': {
#                             'exist': cfup[0],
#                             'cd': cfup[1][0],
#                             'line': cfup[1][1]
#                         }
#                     }), 200
#                 else:
#                     return jsonify({'status': 'success', 'unfinished': {'exist': False, 'cd': ''}}), 200
#             else:
#                 raise

#             return jsonify({'status': 'success', 'percentage': percentage}), 200
#         except Exception as e:
#             log.error('ERROR in printing: %s' % e)
#             # print('ERROR in printing: ', e)
#             return Response(status=500)

#     elif request.method == 'DELETE':
#         try:
#             printer.delete_last_print_files()
#             return Response(status=200)
#         except Exception as e:
#             log.error('ERROR in deleting file (maybe not bad) %s' % e)
#             return Response(status=500)


# @app.route('/api/ip', methods=['POST'])
# def ip_list():
#     """
#     POST:
#     {
#         ips: String[]
#     }
#     """
#     try:
#         if request.method == 'POST':

#             if Utils.is_first_time != -1:
#                 Utils.is_first_time += 1

#             if Utils.is_first_time == 2:
#                 Utils.is_first_time = -1
#                 Utils.connect_to_config_file_wifi()

#             ips = Utils.get_ip_list()
#             # print('list of ips:', ips)
#             return jsonify({'ips': ips}), 200
#     except Exception as e:
#         log.error('error in getting ips: %s' % e)
#         # print('error in getting ips:', e)
#         return Response(status=500)
