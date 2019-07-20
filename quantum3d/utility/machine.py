import serial
import time
import threading
import codecs
import os

try:
    import RPi.GPIO as GPIO
except:
    print("RPi Not Recognized")

from .print_time import Time
# from .extended_board import ExtendedBoard
from quantum3d.db import db, pdb
from .gcode_parser import GCodeParser
from quantum3d.constants import BASE_PATH, UPLOAD_PROTOCOL, UPLOAD_FULL_PATH, MACHINE_SETTINGS_KEYS, SensorFilamentDetectionRegion
from quantum3d.utility.cameras import Camera, captureImage


class Machine:
    def __init__(self, machine_port='/dev/ttyUSB0', machine_baudrate=250000, toolhead_number=1):
        """
        :param machine_port:
        for linux base boards something like  '/dev/ttyUSB0'
        for windows base boards something like 'COM2'
        :param machine_baudrate:
        usually is 250000 because of machine-settings-database.db default
        """
        self.base_path = BASE_PATH
        self.machine_baudrate = machine_baudrate
        self.machine_port = machine_port
        self.machine_serial = None
        self.__Gcodes_to_run = []
        self.__Gcodes_return = []
        self.is_locked = False
        self.printing_file = None  # When printing started, it will set to pure filename
        self.pin = None  # When locked, it will be set, when unlocked, it is None
        self.speed = {
            'fan': 0,  # stores the fan status (0: off | 0.5: half | 1: on)
            'feedrate': 100,        # stores the speed of feedrate (number)
            'flow': 100             # stores the speed of the flow (number)
        }

        try:
            self.machine_settings = pdb.get_multiple(MACHINE_SETTINGS_KEYS)
        except:
            print('ERROR -> could not get initial settings.')

        self.time = Time()
        self.Gcode_handler_error_logs = []
        self.extruder_temp = {'current': 0, 'point': 0}
        self.extruder2_temp = {'current': 0, 'point': 0}
        self.bed_temp = {'current': 0, 'point': 0}
        self.print_percentage = 0
        self.__stop_flag = False
        self.__pause_flag = False
        self.__filament_pause_flag = False
        # self.__update_filament = False
        # self.__relay_updated = False
        # self.__relay_state = None
        self.on_the_print_page = False
        self.__Feedrate_speed_percentage = 100
        self.__Travel_speed_percentage = 100
        self.__current_Z_position = 0
        # self.ext_board = None
        self.use_filament_sensor = False
        self.__take_timelapse = False
        self.filament_sensor_pin = 0
        self.filament_sensor_detection_region = SensorFilamentDetectionRegion.FALLING
        self.number_of_extruder = toolhead_number
        self.active_toolhead = 0
        self.current_position = {'X': 0, 'Y': 0, 'Z': 0}

        if pdb.get_key('timelapse'):
            self.start_capture_timelapse()

        if pdb.get_key('filament'):
            self.sensor_filament_init()

        # TODO: if ran in test mode, this should connect to printer simulator
        self.start_machine_connection()

        # send M105 to machine (on a X-second interval) to update temperature values
        self.refresh_temp_interval()

    def get_bed_temp(self):
        return self.bed_temp

    def get_extruder_temp(self):
        return self.extruder_temp

    def get_extruder2_temp(self):
        return self.extruder2_temp

    def start_machine_connection(self):
        """
        :return:
        True as connected
        False as not connected
        """

        # '''      check for extended board     '''
        # try:
        #     self.ext_board = ExtendedBoard()
        #     self.use_ext_board = True
        # except BaseException as e:
        #     print("extended board connection error: ", e)
        #     self.use_ext_board = False

        try:
            self.machine_serial = serial.Serial(
                port=self.machine_port,
                baudrate=self.machine_baudrate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            self.machine_serial.close()
            self.machine_serial.open()
            time.sleep(2)
            self.machine_serial.write(b'G00\n')
            while True:
                text = str(self.machine_serial.readline())
                if text.find('ok') != -1:
                    break

            gcode_handler_thread = threading.Thread(
                target=self.__Gcode_handler)
            gcode_handler_thread.start()
            return True, None
        except Exception as e:
            print('error in start_machine_connection', e)
            return False, e

    def __Gcode_handler(self):
        """
        this method is for send gcodes on the serial line
        :return:
        """
        first_done = False
        while True:
            try:
                # use_ext_board changed to use_filament_sensor
                # this is for sensor filament
                if self.use_filament_sensor:
                    if self.__filament_pause_flag and not self.__pause_flag:
                        self.__pause_flag = True
                        print("!!! paused by filament error !!!")

                if self.__Gcodes_to_run:
                    gcode_line = (
                        self.__Gcodes_to_run[0] + '\n').encode('utf-8')
                    print('send to machine', gcode_line , self.__Gcodes_return[0] )
                    self.machine_serial.write(gcode_line)
                    if self.__Gcodes_return[0] == 0:
                        while self.machine_serial.readline() != 'ok\n'.encode('utf-8'):
                            pass
                        first_done = True

                    elif self.__Gcodes_return[0] == 1:
                        '''return temp'''
                        if self.number_of_extruder == 2:
                            try:
                                data = self.machine_serial.readline().decode('utf-8')
                                data = GCodeParser.remove_chomp(data)
                                splited = data.split(' ')
                                self.extruder_temp['current'] = float(
                                    splited[1][2:])
                                self.extruder_temp['point'] = float(
                                    splited[2][1:])
                                self.extruder2_temp['current'] = float(
                                    splited[7][3:])
                                self.extruder2_temp['point'] = float(
                                    splited[8][1:])
                                self.bed_temp['current'] = float(
                                    splited[3][2:])
                                self.bed_temp['point'] = float(splited[4][1:])
                            except Exception as e:
                                print("error setting temperatures: ", e)

                        elif self.number_of_extruder == 1:
                            try:
                                data = self.machine_serial.readline().decode('utf-8')
                                data = GCodeParser.remove_chomp(data)
                                splited = data.split(' ')
                                self.extruder_temp['current'] = float(
                                    splited[1][2:])
                                self.extruder_temp['point'] = float(
                                    splited[2][1:])
                                self.bed_temp['current'] = float(
                                    splited[3][2:])
                                self.bed_temp['point'] = float(splited[4][1:])
                            except Exception as e:
                                print("error setting temperatures: ", e)
                        first_done = True

                    elif self.__Gcodes_return[0] == 2:
                        '''return bed temp for mcode M190'''
                        if self.number_of_extruder == 2:
                            data = self.machine_serial.readline().decode('utf-8')
                            data = GCodeParser.remove_chomp(data)
                            while data != 'ok':
                                splited = data.split(' ')
                                self.extruder_temp['current'] = float(
                                    splited[0][2:])
                                self.extruder2_temp['current'] = float(
                                    splited[6][3:])
                                self.bed_temp['current'] = float(
                                    splited[2][2:])
                                data = self.machine_serial.readline().decode('utf-8')
                                data = GCodeParser.remove_chomp(data)
                        elif self.number_of_extruder == 1:
                            data = self.machine_serial.readline().decode('utf-8')
                            data = GCodeParser.remove_chomp(data)
                            while data != 'ok':
                                splited = data.split(' ')
                                self.extruder_temp['current'] = float(
                                    splited[0][2:])
                                self.bed_temp['current'] = float(
                                    splited[2][2:])
                                data = self.machine_serial.readline().decode('utf-8')
                                data = GCodeParser.remove_chomp(data)
                        first_done = True

                    elif self.__Gcodes_return[0] == 3:
                        '''return ext temp for mcode M109'''
                        if self.number_of_extruder == 2:
                            data = self.machine_serial.readline().decode('utf-8')
                            data = GCodeParser.remove_chomp(data)
                            print('here in m109 reading started with 2 nozzel')
                            while data != 'ok':
                                splited = data.split(' ')
                                self.extruder_temp['current'] = float(
                                    splited[0][2:])
                                self.extruder2_temp['current'] = float(
                                    splited[6][3:])
                                data = self.machine_serial.readline().decode('utf-8')
                                data = GCodeParser.remove_chomp(data)
                        elif self.number_of_extruder == 1:
                            data = self.machine_serial.readline().decode('utf-8')
                            data = GCodeParser.remove_chomp(data)
                            print('here in m109 reading started with 1 nozzel')
                            while data != 'ok':
                                splited = data.split(' ')
                                print(splited)
                                self.extruder_temp['current'] = float(
                                    splited[0][2:])
                                data = self.machine_serial.readline().decode('utf-8')
                                data = GCodeParser.remove_chomp(data)
                        first_done = True

                    elif self.__Gcodes_return[0] == 4:
                        self.take_photo_func()
                        while True:
                            text = str(self.machine_serial.readline())
                            if text.find('ok') != -1:
                                break
                        first_done = True

                    if first_done:
                        self.__Gcodes_to_run.pop(0)
                        self.__Gcodes_return.pop(0)
                        first_done = False
            except Exception as ex:
                print('error in gcode handler!', ex)
                self.Gcode_handler_error_logs.append(ex)
                if len(self.Gcode_handler_error_logs) > 9:
                    print("TOO MUCH ERROR! EXITING...")
                    break

    def __read_file_gcode_lines(self, gcode_file_path, line_to_go=0):
        """
        :param gcode_file_path:
        the path of the gcode file
        :param line_to_go:
        start to print from wich line
        :return:
        None
        """
        '''initialize'''
        self.print_percentage = 0
        self.z_pos_offset = 0
        self.__stop_flag = False
        self.__pause_flag = False
        self.on_the_print_page = True
        self.speed['feedrate'] = 100
        self.speed['flow'] = 100
        command = None
        z_pos_offset = 0
        e_pos_offset = 0
        self.__current_Z_position = 0
        gcode_file = codecs.open(gcode_file_path, 'r')
        lines = []
        X_pos, Y_pos = 0, 0

        ''' read files lines'''
        for line in gcode_file:
            gcode = GCodeParser.remove_comment(GCodeParser.remove_chomp(line))
            if gcode != None:
                lines.append(gcode)

        ''' hibernate mode '''

        
        if line_to_go != 0:

            '''                   first heat up the nozzles and bed                  '''
            print('\n\n\nhibernate mode started:\n\n\n')
            
            '''get the extruder temp from the gcode'''
            for line in lines:
                parse_line = GCodeParser.parse(line)
                if 'T' in parse_line:
                    self.active_toolhead = int(parse_line['T'])
                elif 'M' in parse_line:
                    if parse_line['M'] == '109':
                        if 'T' in parse_line:
                            if parse_line['T'] == 0:
                                self.extruder_temp['point'] = int(
                                    float(parse_line['S']))
                                self.append_gcode('M109 S%f T0' % (
                                    self.extruder_temp['point']), 3)
                            elif parse_line['T'] == 1:
                                self.extruder2_temp['point'] = int(
                                    float(parse_line['S']))
                                self.append_gcode('M109 S%f T1' % (
                                    self.extruder2_temp['point']), 3)
                        else:
                            if self.active_toolhead == 0:
                                self.extruder_temp['point'] = int(
                                    float(parse_line['S']))
                                self.append_gcode('M109 S%f T0' % (
                                    self.extruder_temp['point']), 3)
                            elif self.active_toolhead == 1:
                                self.extruder2_temp['point'] = int(
                                    float(parse_line['S']))
                                self.append_gcode('M109 S%f T1' % (
                                    self.extruder2_temp['point']), 3)
                
                print('\n\n\nactive toolhead: ',self.active_toolhead,' T1 :',self.extruder_temp['point'],' T2 :',self.extruder2_temp['point'],'\n\n\n')
                    # break ## search in all the gcode lines because the second nozzel could be in any line

            '''get the bed temp from the gcode'''
            for line in lines:
                parse_line = GCodeParser.parse(line)
                if 'M' in parse_line:
                    if parse_line['M'] == '190':
                        self.bed_temp['point'] = int(float(parse_line['S']))
                        self.append_gcode('M190 S%f' %
                                          (self.bed_temp['point']), 2)
                    break
            print('\n\n\nbed temp : ',self.bed_temp['point'],'\n\n\n')
            '''               second smart hibernate                          '''
            
            algorithm = pdb.get_key('smart_hibernate_algorithm')
            print ('smart hibernate started the algorithm is : ',algorithm)
            # TODO: SHB - the addresses must be dynamic 
            if algorithm == 'circular':
                self.__read_file_gcode_lines('./smart_hibernate_algorithms/Circular_pattern.gcode')
            elif algorithm == 'linear':
                self.__read_file_gcode_lines('./smart_hibernate_algorithms/linear_pattern.gcode')

            '''                     third homing                              '''
            self.append_gcode('G91')
            self.append_gcode('G1 Z%f F%f' % (
                self.machine_settings['hibernate_Z_offset'], self.machine_settings['hibernate_Z_move_feedrate']))
            self.append_gcode('G28 X Y')
            self.append_gcode('G90')

            '''find the layer that had been printed'''
            for i in range(len(lines)):
                try:
                    parse_line = GCodeParser.parse(lines[i])
                    if 'L' in parse_line:
                        if line_to_go == int(parse_line['L']):
                            line_to_go = i
                            break

                except Exception as e:
                    print('error in find line: ', e)

            '''send the nozzle to the correct position to start printing'''
            self.append_gcode('G91')
            self.append_gcode(
                'G1 -Z%f F%f' % (self.machine_settings['hibernate_Z_offset'], self.machine_settings['hibernate_Z_move_feedrate']))
            self.append_gcode('G90')

        ''' gcode applicator '''
        for x in range(line_to_go, len(lines)):

            '''wait for buffer to be free'''
            while len(self.__Gcodes_to_run) >= self.machine_settings['printing_buffer']:
                ''' stop printing when it is waiting in buffer'''
                if self.__stop_flag:
                    break
                time.sleep(0.1)  # wait 100 ms to reduce cpu usage

            # if self.use_ext_board :
            #     '''   check for existance of filament   '''
            #     if self.ext_board.check_filament_status() == False:
            #         self.__pause_flag = True
            #         self.__filament_pause_flag = True
            #         print ('!!! paused by filament error !!!')

            try:
                signnum = lines[x].find(';')
                if not lines[x]:
                    pass
                elif signnum == -1:
                    command = lines[x]
                elif signnum == 0:
                    command = -1
                else:
                    command = GCodeParser.remove_comment(lines[x])

                print('the cleaned command is : ',command)
                '''gcode sending to printer'''
                if command:

                    ''' use command '''

                    parse_command = GCodeParser.parse(command)

                    if 'T' in parse_command:  # T code
                        self.active_toolhead = int(parse_command['T'])

                    if 'L' in parse_command:  # layer we found in gcode remove comment
                        backup_print = open('backup_print.bc', 'w')
                        backup_print.write(parse_command['L'])
                        print('layer found %s' % parse_command['L'])
                        backup_print.close()
                        self.check_timelapse_status(X_pos, Y_pos)
                        command = -1

                    elif 'M' in parse_command:  # M codes

                        if parse_command['M'] == '190':  # for M190
                            self.bed_temp['point'] = int(
                                float(parse_command['S']))
                            self.append_gcode('M190 S%f' %
                                              (self.bed_temp['point']), 2)

                        elif parse_command['M'] == '109':  # for M109
                            if 'T' in parse_command:
                                if parse_command['T'] == 0:
                                    self.extruder_temp['point'] = int(
                                        float(parse_command['S']))
                                    self.append_gcode('M109 S%f T0' % (
                                        self.extruder_temp['point']), 3)
                                elif parse_command['T'] == 1:
                                    self.extruder2_temp['point'] = int(
                                        float(parse_command['S']))
                                    self.append_gcode('M109 S%f T1' % (
                                        self.extruder2_temp['point']), 3)
                            else:
                                if self.active_toolhead == 0:
                                    self.extruder_temp['point'] = int(
                                        float(parse_command['S']))
                                    self.append_gcode('M109 S%f T0' % (
                                        self.extruder_temp['point']), 3)
                                elif self.active_toolhead == 1:
                                    self.extruder2_temp['point'] = int(
                                        float(parse_command['S']))
                                    self.append_gcode('M109 S%f T1' % (
                                        self.extruder2_temp['point']), 3)

                        elif parse_command['M'] == '106':  # for M106
                            self.speed['fan'] = int(float(parse_command['S']))

                        elif parse_command['M'] == '107':  # for M107
                            self.speed['fan'] = 0

                        elif parse_command['M'] == '220':  # for M220
                            self.speed['feedrate'] = int(
                                float(parse_command['S']))

                        elif parse_command['M'] == '221':  # for M221
                            self.speed['flow'] = int(float(parse_command['S']))

                        elif parse_command['M'] == '0':  # for M0
                            pass

                    elif 'G' in parse_command:  # G codes

                        if parse_command['G'] == '1':  # for G1

                            '''                  find and replace E in Gcode              '''
                            if 'E' in parse_command:

                                '''get the last e before the machine trun off'''
                                if e_pos_offset == 0 and line_to_go != 0:
                                    e_pos_offset = float(parse_command['E'])

                                '''get the current e position of file'''
                                new_e_pos = float(parse_command['E'])
                                if line_to_go != 0:
                                    new_e_pos = new_e_pos - e_pos_offset
                                parse_command['E'] = str(new_e_pos)
                                command = GCodeParser.rebuild_gcode(
                                    parse_command)

                            '''         find and replace Z in Gcode               '''
                            '''         this added for simplify              '''
                            if 'Z' in parse_command:

                                '''get the last z before the machine trun off'''
                                if z_pos_offset == 0 and line_to_go != 0:
                                    z_pos_offset = float(parse_command['Z'])

                                '''get the current z position of file'''
                                z_pos = float(parse_command['Z'])
                                if line_to_go != 0:
                                    z_pos = z_pos - z_pos_offset
                                self.__current_Z_position = z_pos
                                parse_command['Z'] = str(z_pos)
                                command = GCodeParser.rebuild_gcode(
                                    parse_command)

                            '''         get x position            '''
                            if 'X' in parse_command:
                                X_pos = float(parse_command['X'])

                            '''         get Y position            '''
                            if 'Y' in parse_command:
                                Y_pos = float(parse_command['Y'])

                        if parse_command['G'] == '0':  # for G0

                            '''         find and replace Z in Gcode               '''
                            '''         this added for cura              '''
                            if 'Z' in parse_command:

                                '''get the last z before the machine trun off'''
                                if z_pos_offset == 0 and line_to_go != 0:
                                    z_pos_offset = float(parse_command['Z'])

                                '''get the current z position of file'''
                                z_pos = float(parse_command['Z'])
                                if line_to_go != 0:
                                    z_pos = z_pos - z_pos_offset
                                self.__current_Z_position = z_pos
                                parse_command['Z'] = str(z_pos)
                                command = GCodeParser.rebuild_gcode(
                                    parse_command)
                    if command != -1:
                        self.append_gcode(command)
                    command = None
            except Exception as e:
                print("error inside read_file_gcode: ", e)

            self.print_percentage = int(float(x + 1) / float(len(lines)) * 100)

            ''' pause and resume the printing '''
            if self.__pause_flag:

                self.append_gcode('G91')
                self.append_gcode('G1 Z%f F%f' % (self.machine_settings['pause_Z_offset'],
                                                  self.machine_settings['pause_Z_move_feedrate']))

                self.append_gcode('G90')

                self.append_gcode('G1 X%d Y%d' % (
                    self.machine_settings['X_pause_position'], self.machine_settings['Y_pause_position']))

                while self.__pause_flag:
                    if self.__stop_flag:
                        break
                    time.sleep(0.1)  # wait 100 ms to reduce cpu usage

                '''  go to the last position and then resume printing  '''
                self.append_gcode('G1 X%f Y%f' % (X_pos, Y_pos))

                self.append_gcode('G91')
                self.append_gcode('G1 Z-%f F%f' % (self.machine_settings['pause_Z_offset'],
                                                   self.machine_settings['pause_Z_move_feedrate']))
                self.append_gcode('G90')

            ''' stop printing '''
            if self.__stop_flag:

                self.__Gcodes_to_run = []
                self.__Gcodes_return = []
                break

            """  print done """

        '''      here       '''
        new_print = dict()
        new_print['time'] = str(self.time.read())
        if self.number_of_extruder == 1:
            new_print['temperature'] = (
                'Extruder: ' + str(self.extruder_temp['point']) + ' - Bed: ' + str(self.bed_temp['point']))
        elif self.number_of_extruder == 2:
            new_print['temperature'] = ('Extruder1: ' + str(self.extruder_temp['point']) + 'Extruder2: ' + str(
                self.extruder2_temp['point']) + ' - Bed: ' + str(self.bed_temp['point']))
        new_print['file_name'] = str(self.printing_file)
        # new_print['filament_type'] = None # TO BE SET
        new_print['is_finished'] = 'Yes' if (
            self.print_percentage == 100) else 'No'

        self.finalize_print(new_print)

        # try:
        #   os.remove('backup_print.bc')
        #  os.remove('backup_print_path.bc')
        # self.printing_file = None
        # except Exception as e:
        #   print('error in reading file lines: ', e)
        #  pass

    def finalize_print(self, new_print):
        self.append_gcode(gcode="M84")  # Release Motors

        # IMAN -> ADDED FOLLOWING LINE FOR DELETING BACK UP FILES
        self.delete_last_print_files()
        self.on_the_print_page = False
        self.printing_file = None

        print_info = (new_print['time'], new_print['temperature'],
                      new_print['file_name'], new_print['is_finished'],)
        db.add_print_info(print_info)

    def append_gcode(self, gcode, gcode_return=0):
        """
        append the gcode to the private var to be sent in the thread
        :param gcode:
        a single line of gcode
        :param gcode_return:
        what kind of data return that gcode
        0 -> nothing
        1 -> temp
        2 -> bed temp(M190)
        3 -> ext temp(M109)
        :return:
        """
        self.__Gcodes_to_run.append(gcode)
        self.__Gcodes_return.append(gcode_return)

    ''' Methods to control the printer '''

    def Home_machine(self, axis='All'):
        """

        :param axis:
        the axis to home
        X Y Z All
        :return:
        """
        if axis == 'All':
            self.append_gcode(gcode='G28 X Y Z')
        elif axis == 'X':
            self.append_gcode(gcode='G28 X')
        elif axis == 'Y':
            self.append_gcode(gcode='G28 Y')
        elif axis == 'Z':
            self.append_gcode(gcode='G28 Z')

    def release_motors(self):
        self.append_gcode(gcode="M84")

    def fan_status(self, status='ON'):
        """
        :param status:
        ON for 255 speed for fan
        Half for 127 speed for fan
        OFF for 0 speed for fan
        :return:
        """
        if status == 'ON':
            self.append_gcode('M106 S255')
            self.speed['fan'] = 1
        elif status == 'Half':
            self.append_gcode('M106 S127')
            self.speed['fan'] = 0.5
        elif status == 'OFF':
            self.append_gcode('M107')
            self.speed['fan'] = 0

    def move_axis(self, axis, positioning_mode, value):
        """
        :param axis:
        X
        Y
        Z
        :param positioning_mode:
        Relative for G91
        Absolute for G90
        :param value:
        the value to be applied
        :return:
        """
        if positioning_mode == 'Relative':
            self.append_gcode(gcode='G91')
        elif positioning_mode == 'Absolute':
            self.append_gcode(gcode='G90')
        gcode = 'G1 %s%f' % (axis, value)
        self.append_gcode(gcode=gcode)

    def extrude(self, value, feedrate=1000):
        """
        :param feedrate:
        the speed of extruder
        :param value:
        the value to be applied
        :return:
        """
        self.append_gcode(gcode='G91')
        gcode = 'G1 E%f F%f' % (value, feedrate)
        self.append_gcode(gcode=gcode)

    def cooldown_hotend(self):
        self.append_gcode(gcode='M104 S0')

    def cooldown_bed(self):
        self.append_gcode(gcode='M140 S0')

    def set_hotend_temp(self, value, toolhead_number=0):
        selected_extruder = self.extruder2_temp if toolhead_number == 1 else self.extruder_temp
        if value + selected_extruder['point'] > 0:
            self.append_gcode(gcode='M104 S%d T%d' % (value, toolhead_number))
        else:
            self.append_gcode(gcode='M104 S0 T%d' % toolhead_number)

    def set_bed_temp(self, value):
        if value+self.bed_temp['point'] > 0:
            # +self.bed_temp['point']))
            self.append_gcode(gcode='M140 S%d' % value)
        else:
            self.append_gcode(gcode='M140 S0')

    def bedleveling_manual(self, stage):
        """
        :param stage:
        1 2 3 4
        |-------------------|
        |         |         |
        |    1    |   2     |
        |-------------------|
        |         |         |
        |   3     |   4     |
        |-------------------|
        :return:
        """
        if stage == 1:
            self.append_gcode(gcode='G91')
            gcode = 'G1 Z%f F%f' % (
                self.machine_settings['bedleveling_Z_offset'], self.machine_settings['bedleveling_Z_move_feedrate'])
            self.append_gcode(gcode=gcode)
            self.append_gcode(gcode='G90')
            gcode = 'G1 X%d Y%d F%f' % (
                self.machine_settings['bedleveling_X1'], self.machine_settings['bedleveling_Y1'], self.machine_settings['traveling_feedrate'])
            self.append_gcode(gcode=gcode)
            self.append_gcode(gcode='G1 Z0')

        if stage == 2:
            self.append_gcode(gcode='G91')
            gcode = 'G1 Z%f F%f' % (
                self.machine_settings['bedleveling_Z_offset'], self.machine_settings['bedleveling_Z_move_feedrate'])
            self.append_gcode(gcode=gcode)
            self.append_gcode(gcode='G90')
            gcode = 'G1 X%d Y%d F%f' % (
                self.machine_settings['bedleveling_X2'], self.machine_settings['bedleveling_Y1'], self.machine_settings['traveling_feedrate'])
            self.append_gcode(gcode=gcode)
            self.append_gcode(gcode='G1 Z0')

        if stage == 3:
            self.append_gcode(gcode='G91')
            gcode = 'G1 Z%f F%f' % (
                self.machine_settings['bedleveling_Z_offset'], self.machine_settings['bedleveling_Z_move_feedrate'])
            self.append_gcode(gcode=gcode)
            self.append_gcode(gcode='G90')
            gcode = 'G1 X%d Y%d F%f' % (
                self.machine_settings['bedleveling_X1'], self.machine_settings['bedleveling_Y2'], self.machine_settings['traveling_feedrate'])
            self.append_gcode(gcode=gcode)
            self.append_gcode(gcode='G1 Z0')

        if stage == 4:
            self.append_gcode(gcode='G91')
            gcode = 'G1 Z%f F%f' % (
                self.machine_settings['bedleveling_Z_offset'], self.machine_settings['bedleveling_Z_move_feedrate'])
            self.append_gcode(gcode=gcode)
            self.append_gcode(gcode='G90')
            gcode = 'G1 X%d Y%d F%f' % (
                self.machine_settings['bedleveling_X2'], self.machine_settings['bedleveling_Y2'], self.machine_settings['traveling_feedrate'])
            self.append_gcode(gcode=gcode)
            self.append_gcode(gcode='G1 Z0')

    def refresh_temp(self):
        self.append_gcode('M105', 1)

    def refresh_temp_interval(self):
        t = threading.Timer(2, self.refresh_temp_interval)
        t.daemon = True
        t.start()
        self.refresh_temp()

    ''' print 
        gcode_dir: '<UPLOAD_PROTOCOL><GCODE_FILE_NAME>' or '<PATH_TO_GCODE_FILE_NAME_IN_USB>'
    '''

    def start_printing_thread(self, gcode_dir, line=0):
        self.time = Time()
        self.printing_file = str(gcode_dir).split(os.path.sep)[-1]


        if str(gcode_dir).startswith(UPLOAD_PROTOCOL):
            gcode_dir = os.path.join(UPLOAD_FULL_PATH,
                                     gcode_dir[len(UPLOAD_PROTOCOL):])
        else:
            gcode_dir = os.path.join(self.base_path, gcode_dir)


        '''get a backup from gcode file path for hibernate '''
        with open('backup_print_path.bc', 'w') as backup_print:
            backup_print.write(gcode_dir)

            
        # gcode_dir is now the COMPLETE FULL PATH to the file
        print('@@@ printing file dir:', gcode_dir)
        read_file_gcode_lines_thread = threading.Thread(
            target=self.__read_file_gcode_lines, args=(gcode_dir, line,))

        # ''' refresh the  ext board buffer to able get the filament error '''
        # if self.use_ext_board:
        #     self.ext_board.flush_input_buffer()
        #     self.ext_board.off_A_flag()

        read_file_gcode_lines_thread.start()
        print('started')

    def stop_printing(self):
        self.__stop_flag = True
        self.on_the_print_page = False

    def pause_printing(self):
        self.__pause_flag = True

    def resume_printing(self):
        # self.__pause_flag = False
        # self.__filament_pause_flag = False
        if self.use_filament_sensor:
            # oprator pressed resume but not inserted the filament
            if not self.check_for_filament_manually(self.filament_sensor_pin):
                self.__pause_flag = True
                self.__filament_pause_flag = True
            else:
                self.__pause_flag = False
                self.__filament_pause_flag = False
        else:

            self.__pause_flag = False
            self.__filament_pause_flag = False

    def get_percentage(self):
        return self.print_percentage

    """ Feedrate means changes speed on X, Y,Z and E axis """

    def set_feedrate_speed(self, percentage):
        #self.__Feedrate_speed_percentage = percentage
        self.append_gcode(gcode='M220 S%d' % (percentage))
        self.speed['feedrate'] = percentage

    """ Flow means changes speed on only E axis """

    def set_flow_speed(self, percentage):
        #self.__Travel_speed_percentage = percentage
        self.append_gcode(gcode='M221 S%d' % (percentage))
        self.speed['flow'] = percentage

    def get_current_Z_position(self):
        """
        return Z positon acording to Gcode lines 
        never run this if machine is not in 'printing' state 
        """
        return "%.1f" % self.__current_Z_position

    def check_for_unfinished_print(self):
        """
        checking for unfinished work for hibernate situation
        :return:
        if there was any unfinishd job it first return TRUE and return a array of [unfinished gcode file path , the last printed line ]
        if there was no unfinishd job it returns FALSE , NONE
        """
        try:
            backup_print = open('backup_print.bc', 'r')
            backup_print_path = open('backup_print_path.bc', 'r')
            backup_file_path = backup_print_path.readline()
            backup_line = int(backup_print.readline())
            print("backup file and line: ", backup_file_path, backup_line)
            backup_print.close()
            backup_print_path.close()
            return True, [backup_file_path, backup_line]
        except Exception as e:
            print("error returning backup files and lines: ", e)
            return False, None

    def delete_last_print_files(self):
        try:
            os.remove('backup_print.bc')
            os.remove('backup_print_path.bc')
            pdb.set_key('sc_index', 0)
        except:
            print("file not removed!")

    def stop_move_up(self):
        self.append_gcode('G91')
        self.append_gcode('G1 Z%f F%f' % (self.machine_settings['pause_Z_offset'],
                                          self.machine_settings['pause_Z_move_feedrate']))
        self.append_gcode('G90')

    '''       sensor filament methodes     '''

    def is_filament(self):
        return self .__filament_pause_flag

    def sensor_filament_init(self, BCM_pin_number=4):
        # for filament sensor
        self.filament_sensor_pin = BCM_pin_number
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)

            if self.filament_sensor_detection_region == SensorFilamentDetectionRegion.FALLING:
                GPIO.setup(BCM_pin_number, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                GPIO.add_event_detect(BCM_pin_number, GPIO.FALLING,
                                      callback=self.filament_sensor_event, bouncetime=300)
            elif self.filament_sensor_detection_region == SensorFilamentDetectionRegion.RISING:
                GPIO.setup(BCM_pin_number, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(BCM_pin_number, GPIO.RISING,
                                      callback=self.filament_sensor_event, bouncetime=300)

            self.use_filament_sensor = True
        except Exception as e:
            print('error in sensor_filament_init', e)

    def disable_sensor_filament(self):
        try:
            GPIO.cleanup()           # clean up GPIO
            self.use_filament_sensor = False
        except Exception as e:
            print('error in disable_sensor_filament', e)

    def filament_sensor_event(self, channel):
        try:
            if self.filament_sensor_detection_region == SensorFilamentDetectionRegion.FALLING:
                if GPIO.input(self.filament_sensor_pin) == 0:
                    self.__filament_pause_flag = True
                    print('!!! filament sensor event called !!!')
            elif self.filament_sensor_detection_region == SensorFilamentDetectionRegion.RISING:
                if GPIO.input(self.filament_sensor_pin) == 1:
                    self.__filament_pause_flag = True
                    print('!!! filament sensor event called !!!')
        except Exception as e:
            print("error in filament sensor event: ", e)

    def check_for_filament_manually(self, BCM_pin_number):
        try:
            if self.filament_sensor_detection_region == SensorFilamentDetectionRegion.FALLING:
                if GPIO.input(BCM_pin_number):  # on HIGH
                    return True
                else:  # on LOW
                    self.__filament_pause_flag = True
                    print('!!! filament manually detected no filament !!!')
                    return False
            elif self.filament_sensor_detection_region == SensorFilamentDetectionRegion.RISING:
                if not GPIO.input(BCM_pin_number):  # on LOW
                    return True
                else:  # on HIGH
                    self.__filament_pause_flag = True
                    print('!!! filament manually detected no filament !!!')
                    return False
        except Exception as e:
            print('error in check_for_filament_manually', e)

    '''    two nozzles methodes       '''

    def select_extruder(self, ext_num):
        self.append_gcode('T%d' % (ext_num))

    '''  timelapse methodes '''

    def start_capture_timelapse(self):
        self.__take_timelapse = True
        camera_thread = threading.Thread(target=self.__capture_dummy_frame)
        camera_thread.start()

    # to let the camera stay on
    def __capture_dummy_frame(self):
        print("!!! init timelapse camera !!!")
        try:
            cam = pdb.get_key('selected_camera')
            if not cam:
                print("no initial camera for timelapse")
                return
            camera = Camera[cam]()

            while self.__take_timelapse:
                frame = camera.get_frame()
                yield frame
            return
        except Exception as e:
            print("capture dummy frame error: ", e)
        print("!!! end timelapse camera !!!")

    def end_capture_timelapse(self):
        self.__take_timelapse = False

    def move_ext_for_take_photo(self, x_pos, y_pose):
        self.append_gcode('G90')
        self.append_gcode('G1 X%f Y%f' % (x_pos, y_pose))

    def retract_nozzel(self, sign):
        self.append_gcode('G91')
        self.append_gcode('G1 E%s%d F%d' % (
            sign, self.machine_settings['retraction_offset'], self.machine_settings['retraction_feedrate']))
        self.append_gcode('G90')

    def take_photo_gcode(self):
        self.append_gcode('G4 P%d' % self.machine_settings['delay_time'])
        self.append_gcode('G4 P%d' % self.machine_settings['delay_time'], 4)

    def take_photo_func(self):
        captureImage()

    def check_timelapse_status(self, current_x, current_y):
        if self.__take_timelapse:
            self.retract_nozzel('-')
            self.move_ext_for_take_photo(
                self.machine_settings['X_timelapse_position'], self.machine_settings['Y_timelapse_position'])
            self.take_photo_gcode()
            self.move_ext_for_take_photo(current_x, current_y)
            self.retract_nozzel('+')

    '''    handwheel methodes       '''

    def set_handwheel_offset_position(self, X_pos=0, Y_pos=0, Z_pos=0):
        self.append_gcode('M206 X-%d Y-%d Z-%d' % (X_pos, Y_pos, Z_pos))

    def deactive_handwheel_offset_position(self):
        self.append_gcode('M206 X0 Y0 Z0')

    def get_current_position(self):  # TODO: update it
        return self.current_position
