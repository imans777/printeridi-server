from flask import request, json, Response, jsonify, abort
import time

from quantum3d.routes import api_bp as app
from quantum3d.utility import printer
from quantum3d.db import pdb


@app.route('/print', methods=['DELETE', 'POST'])
def printing():
    """
    POST:
        Request: {
            action: 'print' | 'stop' | 'pause' | 'resume' | 'percentage' | 'unfinished'
            cd: string, (only if it was print)
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

            ''' refresh the  ext board buffer to able get the filament error '''
            if printer.use_ext_board:
                printer.ext_board.flush_input_buffer()
                printer.ext_board.off_A_flag()

            ''' delete last printed back up files '''
            printer.delete_last_print_files()
            gcode_file_address = req['cd']
            if printer.base_path in gcode_file_address:
                gcode_file_address = gcode_file_address[
                    len(printer.base_path)+1:
                ]
            if 'line' in req:
                printer.start_printing_thread(
                    gcode_dir=gcode_file_address,
                    line=req['line']
                )
            else:
                printer.start_printing_thread(gcode_dir=gcode_file_address)
            # TODO: put the file inside uploads files and print from there to avoid usb crash, etc.!
        elif action == 'stop':
            if not printer.on_the_print_page:
                abort(403)

            pdb.set_key('is_paused', 0)
            printer.stop_printing()
            printer.delete_last_print_files()
            ''' wait until the buffer becomes free '''
            time.sleep(1)
            printer.release_motors()
            printer.cooldown_hotend()
            printer.cooldown_bed()
            printer.stop_move_up()
        elif action == 'resume':
            if not printer.on_the_print_page:
                abort(403)

            pdb.set_key('is_paused', 0)
            printer.resume_printing()
        elif action == 'pause':
            if not printer.on_the_print_page:
                abort(403)

            pdb.set_key('is_paused', 1)
            printer.pause_printing()
        elif action == 'percentage':
            if not printer.on_the_print_page:
                abort(403)

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
        printer.delete_last_print_files()
        return Response(status=200)
