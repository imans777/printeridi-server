from flask import request, json, Response, jsonify, abort
import time
import os

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer, Utils
from quantum3d.db import pdb
from quantum3d.constants import PrintStatus, UPLOAD_PROTOCOL, UPLOAD_FULL_PATH


@app.route('/print', methods=['DELETE', 'POST'])
def printing():
    """
    POST:
        Request: {
            action: 'print' | 'stop' | 'pause' | 'resume' | 'percentage' | 'unfinished'
            cd: string, (only if it was print) ('upload://FILENAME' | 'PATH_TO_FILE')
            line: number (Optional)
        }
        Response (default): {
            status: 'success' | 'failure'
            percentage: Number
        }
        Response (unfinished): {
            status: 'success' | 'failure'
            unfinished: {
                exist: True | False,
                (if exist:)
                cd: String,
                line: Number
            }
        }

    DELETE:
    {}{}

    """
    if request.method == 'POST':
        req = request.json
        action = req['action']
        percentage = 0

        if action == 'print':
            if printer.on_the_print_page:
                abort(403)
            print_start(req)

        elif action == 'stop':
            if not printer.on_the_print_page:
                abort(403)
            print_stop()

        elif action == 'resume':
            if not printer.on_the_print_page:
                abort(403)
            print_resume()

        elif action == 'pause':
            if not printer.on_the_print_page:
                abort(403)
            print_pause()

        elif action == 'percentage':
            percentage = printer.get_percentage()

        elif action == 'unfinished':
            if printer.on_the_print_page:
                abort(403)
            cfup = printer.check_for_unfinished_print()
            if cfup[0] == True:
                return jsonify({
                    'status': 'success',
                    'unfinished': {
                        'exist': cfup[0],
                        'cd': cfup[1][0],
                        'line': cfup[1][1]
                    }
                }), 200
            else:
                return jsonify({
                    'status': 'success',
                    'unfinished': {
                        'exist': False,
                        'cd': ''
                    }
                }), 200
        else:
            abort(403)

        return jsonify({
            'status': 'success',
            'percentage': percentage
        }), 200

    elif request.method == 'DELETE':
        print_delete_files()
        return Response(status=200)


def print_start(req):
    # TODO: maybe put the file inside uploads folder
    # and print from there to avoid usb crash, etc.!
    print_delete_files()

    gcode_file_address = req['cd']

    ip = Utils.get_ip_list()
    gcode_file_link = 'http://{}/api/download/'.format(
        len(ip) and ip[0] or 'localhost')

    if str(gcode_file_address).startswith(UPLOAD_PROTOCOL):
        gcode_file_link += 'files/' + gcode_file_address[len(UPLOAD_PROTOCOL):]
    else:
        gcode_file_link += 'usbs/' + gcode_file_address

    # set file dir and gcode link in db after modifications
    pdb.set_key('print_file_dir', gcode_file_address)
    pdb.set_key('gcode_downloadable_link', gcode_file_link)

    printer.start_printing_thread(gcode_dir=gcode_file_address,
                                  line=req.get('line') or 0)


def print_stop():
    pdb.set_key('print_status', PrintStatus.IDLE.value)
    printer.stop_printing()
    print_delete_files()

    ''' wait until the buffer becomes free '''
    time.sleep(1)

    printer.release_motors()
    printer.cooldown_hotend()
    printer.cooldown_bed()
    printer.stop_move_up()


def print_resume():
    pdb.set_key('print_status', PrintStatus.PRINTING.value)
    printer.resume_printing()


def print_pause():
    pdb.set_key('print_status', PrintStatus.PAUSED.value)
    printer.pause_printing()


def print_delete_files():
    ''' delete last printed back up files '''
    printer.delete_last_print_files()
