"""
Machine utils for printer connection 
programmer = SHB
company = Persia3DPrinter (http://persia3dprinter.ir/)
"""

import serial
import time
import threading
import subprocess
import codecs
import os
#import psutil
import sqlite3
import configparser


import logging
LOG_LEVEL = logging.DEBUG
LOGFORMAT = "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
from colorlog import ColoredFormatter
logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOGFORMAT)
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
log = logging.getLogger('pythonConfig')
log.setLevel(LOG_LEVEL)
log.addHandler(stream)


BASE_PATH = '/media/pi'  # '/media/pi'   '''** change for test in laptop or raspberry pi   '''


class Machine:
    def __init__(self, machine_port='/dev/ttyUSB0', machine_baudrate=250000):
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
        self.printing_file = None  # When printing started, it will set to filename
        self.pin = None  # When locked, it will be set, when unlocked, it is None

        db = sqlite3.connect(
            'database.db', check_same_thread=False, isolation_level=None)
        self.dbcursor = db.cursor()
        # settings_keys = ('bedleveling_X1', 'bedleveling_X2',
        #                  'bedleveling_Y1', 'bedleveling_Y2',
        #                  'traveling_feedrate', 'bedleveling_Z_ofsset',
        #                  'bedleveling_Z_move_feedrate', 'hibernate_Z_offset',
        #                  'hibernate_Z_move_feedrate', 'pause_Z_offset',
        #                  'pause_Z_move_feedrate', 'printing_buffer',
        #                  'ABS', 'pin')

        self.dbcursor.execute('''CREATE TABLE IF NOT EXISTS Settings
        (bedleveling_X1 real, bedleveling_X2 real,
        bedleveling_Y1 real, bedleveling_Y2 real,
        traveling_feedrate real, bedleveling_Z_ofsset real,
        bedleveling_Z_move_feedrate real, hibernate_Z_offset real,
        hibernate_Z_move_feedrate real, pause_Z_offset real,
        pause_Z_move_feedrate real, printing_buffer real,
        ABS TEXT, pin real)''')

        self.dbcursor.execute('SELECT * FROM Settings LIMIT 1')
        settings = self.dbcursor.fetchone()
        if settings is None:
            settings = (50, 180, 50, 180, 3000, 10, 1500,
                        5, 1500, 10, 1500, 15, "yes", None,)
            self.dbcursor.execute("""INSERT INTO Settings
                                  (bedleveling_X1, bedleveling_X2,
                                  bedleveling_Y1, bedleveling_Y2,
                                  traveling_feedrate, bedleveling_Z_ofsset,
                                  bedleveling_Z_move_feedrate, hibernate_Z_offset,
                                  hibernate_Z_move_feedrate, pause_Z_offset,
                                  pause_Z_move_feedrate, printing_buffer, ABS, pin)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", settings)

        self.machine_settings = {
            # manual bed leveling settings
            'bedleveling_X1': settings[0], 'bedleveling_X2': settings[1], 'bedleveling_Y1': settings[2], 'bedleveling_Y2': settings[3],
            'traveling_feedrate': settings[4],
            'bedleveling_Z_ofsset': settings[5], 'bedleveling_Z_move_feedrate': settings[6],
            # hibernate setting
            'hibernate_Z_offset': settings[7], 'hibernate_Z_move_feedrate': settings[8],
            # pause setting
            'pause_Z_offset': settings[9], 'pause_Z_move_feedrate': settings[10],
            # printing buffer
            'printing_buffer': settings[11],
            # Should the system ask to start previous print after hibernate ("yes") or not ("no")
            'ABS': settings[12],
        }

        self.time = Time()
        self.Gcode_handler_error_logs = []
        self.extruder_temp = {'current': 0, 'point': 0}
        self.bed_temp = {'current': 0, 'point': 0}
        self.print_percentage = 0
        self.__stop_flag = False
        self.__pause_flag = False
        self.__filament_pause_flag = False
        self.__update_filament = False
        self.__relay_updated = False
        self.__relay_state = None
        self.on_the_print_page = False
        self.__Feedrate_speed_percentage = 100
        self.__Travel_speed_percentage = 100
        self.__current_Z_position = 0
        # self.recent_print_status = self.load_recent_print_status() # is a list of tuples
        self.ext_board = None
        self.use_ext_board = False
        self.start_machine_connection()

    def set_pin(self, pin):
        try:
            self.dbcursor.execute('UPDATE Settings SET pin = ?', (pin,))
            print(pin)
            return True
        except Exception as e:
            print('Error in setting pin:', e)
            return False

    def fetch_pin(self):
        print(self.is_locked)
        self.dbcursor.execute('SELECT pin FROM Settings LIMIT 1')
        pin = self.dbcursor.fetchone()[0]
        if pin is None:
            return None
        return int(pin)

    def set_abs(self, status):
        self.dbcursor.execute("UPDATE Settings SET ABS=?", (status,))

    def get_abs(self):
        self.dbcursor.execute("SELECT ABS FROM Settings LIMIT 1")
        return self.dbcursor.fetchone()[0]

    def get_recent_print_status(self):
        result = []
        self.dbcursor.execute('SELECT * FROM Prints LIMIT 10')
        prints = self.dbcursor.fetchall()

        for print_status in prints:
            status = {
                'time': print_status[0],
                'temperature': print_status[1],
                'file_name': print_status[2],
                # 'filament_type': print_status[3],
                # We don't have filament type yet! So we skip this for now!
                'is_finished': print_status[3],
            }
            result.append(status)
        return result

    def get_bed_temp(self):
        return self.bed_temp

    def get_extruder_temp(self):
        return self.extruder_temp

    def start_machine_connection(self):
        """
        :return:
        True as connected
        False as not connected
        """
        '''      check for extended board     '''
        try:
            self.ext_board = ExtendedBoard()
            self.use_ext_board = True
        except BaseException as e:
            print(e)
            self.use_ext_board = False

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
            print(e)
            return False, e

    def __Gcode_handler(self):
        """
        this method is for send gcodes on the serial line
        :return:
        """
        first_done = False
        while True:
            try:

                if self.use_ext_board:
                    if self.__update_filament:
                        '''   check for existance of filament   '''
                        self.__update_filament = False
                        if self.ext_board.check_filament_status() == False:
                            self.__pause_flag = True
                            self.__filament_pause_flag = True
                            print ('!!! paused by filament error !!!')

                    if self.__relay_updated:
                        ''' set relay status '''
                        self.__relay_updated = False
                        self.ext_board.relay_status(
                            self.__relay_state[0], self.__relay_state[1])
                        print ('relay %d status %r' %
                               (self.__relay_state[0], self.__relay_state[1]))

                if self.__Gcodes_to_run:
                    print('send to machine', ('%s%s' %
                                              (self.__Gcodes_to_run[0], '\n')).encode('utf-8'))
                    self.machine_serial.write(
                        (self.__Gcodes_to_run[0] + '\n').encode('utf-8'))
                    if self.__Gcodes_return[0] == 0:
                        while self.machine_serial.readline() != 'ok\n'.encode('utf-8'):
                            pass
                        first_done = True

                    elif self.__Gcodes_return[0] == 1:
                        '''retrun temp'''
                        data = self.machine_serial.readline().decode('utf-8')
                        splited = data.split(' ')
                        self.extruder_temp['current'] = float(splited[1][2:])
                        self.extruder_temp['point'] = float(splited[2][1:])
                        self.bed_temp['current'] = float(splited[3][2:])
                        self.bed_temp['point'] = float(splited[4][1:])

                        first_done = True

                    elif self.__Gcodes_return[0] == 2:
                        '''return bed temp for mcode M190'''
                        data = self.machine_serial.readline().decode('utf-8')
                        while data != 'ok\n':
                            splited = data.split(' ')
                            self.extruder_temp['current'] = float(
                                splited[0][2:])
                            self.bed_temp['current'] = float(splited[2][2:])
                            data = self.machine_serial.readline().decode('utf-8')
                        first_done = True

                    elif self.__Gcodes_return[0] == 3:
                        '''return ext temp for mcode M109'''
                        data = self.machine_serial.readline().decode('utf-8')
                        while data != 'ok\n':
                            splited = data.split(' ')
                            self.extruder_temp['current'] = float(
                                splited[0][2:])
                            data = self.machine_serial.readline().decode('utf-8')
                        first_done = True

                    if first_done:
                        print('in first done')
                        self.__Gcodes_to_run.pop(0)
                        self.__Gcodes_return.pop(0)
                        first_done = False
            except Exception as ex:
                print('error in gcode handler!', ex)
                self.Gcode_handler_error_logs.append(ex)
                if len(self.Gcode_handler_error_logs) > 9:
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
        command = None
        z_pos_offset = 0
        e_pos_offset = 0
        self.__current_Z_position = 0
        gcode_file = codecs.open(gcode_file_path, 'r')
        lines = []

        '''      here       '''
        self.on_the_print_page = True

        '''get a backup from gcode file path for hibernate '''
        with open('backup_print_path.bc', 'w') as backup_print:
            backup_print.write(gcode_file_path)

        ''' read files lines'''
        for line in gcode_file:
            lines.append(line[:-1])

        '''hibernate mode'''
        if line_to_go != 0:

            '''first homing the x and y to resume printing'''
            self.append_gcode('G91')
            self.append_gcode('G1 Z%f F%f' % (
                self.machine_settings['hibernate_Z_offset'], self.machine_settings['hibernate_Z_move_feedrate']))
            self.append_gcode('G28 X Y')
            self.append_gcode('G90')

            '''get the bed temp from the gcode'''
            for line in lines:
                if line.find('M190') == 0:
                    Sfound = line.find('S')
                    if line.find(' ', Sfound) != -1:
                        end = line.find(' ', Sfound)
                    elif line.find('\n', Sfound) != -1:
                        end = line.find('\n')
                    else:
                        end = len(line)
                    self.bed_temp['point'] = int(
                        float(line[line.find('S') + 1: end ]))
                    self.append_gcode('M190 S%f' % (self.bed_temp['point']), 2)
                    end = None 
                    break

            '''get the extruder temp from the gcode'''
            for line in lines:
                if line.find('M109') == 0:
                    Sfound = line.find('S')
                    if line.find(' ', Sfound) != -1:
                        end = line.find(' ', Sfound)
                    elif line.find('\n', Sfound) != -1:
                        end = line.find('\n')
                    else:
                        end = len(line)
                    self.extruder_temp['point'] = int(
                        float(line[line.find('S') + 1: end ]))
                    self.append_gcode('M109 S%f' %
                                      (self.extruder_temp['point']), 3)
                    end = None 
                    break

            '''find the layer that had been printed'''
            for i in range(len(lines)):
                try:
                    if lines[i].find(';LAYER:') == 0:
                        if line_to_go == int(lines[i][7:]):
                            '''get the direct gcode line (the past value was the layer that has been printed)'''
                            line_to_go = i
                    elif lines[i].find('; layer') == 0:
                        if line_to_go == int(lines[i][8:lines[i].find(',')]):
                            '''get the direct gcode line (the past value was the layer that has been printed)'''
                            line_to_go = i
                except Exception as e:print('error in find line :',e)


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

            # if self.use_ext_board :
            #     '''   check for existance of filament   '''
            #     if self.ext_board.check_filament_status() == False:
            #         self.__pause_flag = True
            #         self.__filament_pause_flag = True
            #         print ('!!! paused by filament error !!!')

            signnum = lines[x].find(';')
            if not lines[x]:
                pass
            elif signnum == -1:
                command = lines[x]
            elif signnum == 0:

                cura_layer = lines[x].find(';LAYER:')
                if cura_layer == 0:
                    layer = lines[x][7:]
                    backup_print = open('backup_print.bc', 'w')
                    backup_print.write(layer)
                    backup_print.close()
                
                simplify_layer = lines[x].find('; layer')
                if simplify_layer == 0:
                    layer = lines[x][8:lines[x].find(',')]
                    backup_print = open('backup_print.bc', 'w')
                    backup_print.write(layer)
                    backup_print.close()

            else:
                command = lines[x][:-(len(lines[x]) - signnum)]

            '''gcode sending to printer'''
            if command:

                ''' use command '''

                if command.find('M190') == 0:
                    Sfound = command.find('S')
                    if command.find(' ', Sfound) != -1:
                        end = command.find(' ', Sfound)
                    elif command.find('\n', Sfound) != -1:
                        end = command.find('\n')
                    else:
                        end = len(command)
                    self.bed_temp['point'] = int(
                        float(command[command.find('S') + 1: end ]))
                    self.append_gcode('M190 S%f' % (self.bed_temp['point']), 2)
                    end = None 

                elif command.find('M109') == 0:
                    Sfound = command.find('S')
                    if command.find(' ', Sfound) != -1:
                        end = command.find(' ', Sfound)
                    elif command.find('\n', Sfound) != -1:
                        end = command.find('\n')
                    else:
                        end = len(command)
                    self.extruder_temp['point'] = int(
                        float(command[command.find('S') + 1: end ]))
                    self.append_gcode('M109 S%f' %
                                      (self.extruder_temp['point']), 3)
                    end = None 

                elif command.find('M0') == 0:
                    pass

                elif command.find('G1') == 0:

                    # '''                find and repalce F in Gcode file        '''
                    # Travel_speed = command.find('F')

                    # if Travel_speed != -1:

                    #     # find the number in front of 'F' character
                    #     if command.find(' ', Travel_speed) != -1:
                    #         end = command.find(' ', Travel_speed)
                    #     elif command.find('\n', Travel_speed) != -1:
                    #         end = command.find('\n')
                    #     else:
                    #         end = len(command)

                    #     last_travel_speed = float(
                    #         command[Travel_speed + 1: end])
                    #     new_travel_speed = last_travel_speed * self.__Travel_speed_percentage / 100
                    #     command = command[0:Travel_speed + 1] + str(new_travel_speed) + command[len(
                    #         command[0:Travel_speed]) + len(str(last_travel_speed)) - 1:]
                    #     end = None

                    '''                  find and replace E in Gcode              '''
                    Eresulte = command.find('E')

                    if Eresulte != -1:

                        # find the number in front of 'E' character
                        if command.find(' ', Eresulte) != -1:
                            end = command.find(' ', Eresulte)
                        elif command.find('\n', Eresulte) != -1:
                            end = command.find('\n')
                        else:
                            end = len(command)

                        '''get the last e before the machine trun off'''
                        if e_pos_offset == 0 and line_to_go != 0:
                            e_pos_offset = float(command[Eresulte + 1: end])
                        '''get the current e position of file'''
                        last_e_pos = float(command[Eresulte + 1: end])
                        new_e_pos = last_e_pos
                        if line_to_go != 0:
                            new_e_pos = last_e_pos - e_pos_offset
                        # command = command[:-(len(command) - (Eresulte + 1))] + str(e_pos)
                        command = command[0: Eresulte + 1] + str(new_e_pos) + ' ' + command[len(
                            command[0: Eresulte + 1]) + len(str(last_e_pos)) + 1:]
                        end = None

                    '''         find and replace Z in Gcode               '''
                    '''         this added just for simplify              '''
                    Zresulte = command.find('Z')

                    if Zresulte != -1:
                        
                        if command.find(' ', Zresulte) != -1:
                            end = command.find(' ', Zresulte)
                        elif command.find('\n', Zresulte) != -1:
                            end = command.find('\n')
                        else:
                            end = len(command)

                        '''get the last z before the machine trun off'''
                        if z_pos_offset == 0 and line_to_go != 0:
                            z_pos_offset = float(command[Zresulte + 1: end])
                        '''get the current z position of file'''
                        z_pos = float(command[Zresulte + 1: end ])
                        if line_to_go != 0:
                            z_pos = z_pos - z_pos_offset
                        self.__current_Z_position = z_pos
                        command = command[0: Zresulte + 1] + str(z_pos) + ' ' + command[end + 1:]

                        end = None

                    '''         get x position            '''
                    Xresulte = command.find('X')

                    if Xresulte != -1:
                        
                        if command.find(' ', Xresulte) != -1:
                            end = command.find(' ', Xresulte)
                        elif command.find('\n', Xresulte) != -1:
                            end = command.find('\n')
                        else:
                            end = len(command)

                        X_pos = float(command[Xresulte + 1: end ])

                        end = None
                        
                    '''         get Y position            '''
                    Yresulte = command.find('Y')

                    if Yresulte != -1:
                        
                        if command.find(' ', Yresulte) != -1:
                            end = command.find(' ', Yresulte)
                        elif command.find('\n', Yresulte) != -1:
                            end = command.find('\n')
                        else:
                            end = len(command)

                        Y_pos = float(command[Yresulte + 1: end ])

                        end = None


                    self.append_gcode(command)

                elif command.find('G0') == 0:

                    '''         find and replace Z in Gcode               '''
                    Zresulte = command.find('Z')

                    if Zresulte != -1:
                        
                        if command.find(' ', Zresulte) != -1:
                            end = command.find(' ', Zresulte)
                        elif command.find('\n', Zresulte) != -1:
                            end = command.find('\n')
                        else:
                            end = len(command)

                        '''get the last z before the machine trun off'''
                        if z_pos_offset == 0 and line_to_go != 0:
                            z_pos_offset = float(command[Zresulte + 1: end])
                        '''get the current z position of file'''
                        z_pos = float(command[Zresulte + 1: end ])
                        if line_to_go != 0:
                            z_pos = z_pos - z_pos_offset
                        self.__current_Z_position = z_pos
                        command = command[0: Zresulte + 1] + str(z_pos) + ' ' + command[end + 1:]

                        end = None 

                    # '''                find and repalce F in Gcode file        '''
                    # Feedrate_speed = command.find('F')

                    # if Feedrate_speed != -1:

                    #     # find the number in front of 'F' character
                    #     if command.find(' ', Feedrate_speed) != -1:
                    #         end = command.find(' ', Feedrate_speed)
                    #     elif command.find('\n', Feedrate_speed) != -1:
                    #         end = command.find('\n')
                    #     else:
                    #         end = len(command)

                    #     last_feedrate = float(command[Feedrate_speed + 1: end])
                    #     new_feedrate = last_feedrate * self.__Feedrate_speed_percentage / 100
                    #     command = command[0:Feedrate_speed + 1] + str(new_feedrate) + command[len(
                    #         command[0:Feedrate_speed]) + len(str(last_feedrate)) - 1:]
                    #     end = None

                    self.append_gcode(command)

                else:
                    self.append_gcode(command)
                # if not 
                command = None

            self.print_percentage = int(float(x + 1) / float(len(lines)) * 100)

            ''' pause and resume the printing '''
            if self.__pause_flag:

                self.append_gcode('G91')
                self.append_gcode('G1 Z%f F%f' % (self.machine_settings['pause_Z_offset'],
                                                  self.machine_settings['pause_Z_move_feedrate']))
                self.append_gcode('G28 X Y')
                self.append_gcode('G90')

                while self.__pause_flag:
                    if self.__stop_flag:
                        break

                '''  go to the last position and then resume printing  '''
                self.append_gcode('G1 X%f Y%f'%(X_pos,Y_pos))

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
        new_print['temperature'] = (
            'Extruder: ' + str(self.extruder_temp['point']) + ' - Bed: ' + str(self.bed_temp['point']))
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

        self.dbcursor.execute('''CREATE TABLE IF NOT EXISTS Prints
                    (time TEXT, temperature TEXT, file_name TEXT, is_finished TEXT)
                    ''')
        print_status = (new_print['time'], new_print['temperature'],
                        new_print['file_name'], new_print['is_finished'],)
        self.dbcursor.execute(
            'INSERT INTO Prints VALUES (?, ?, ?, ?)', print_status)

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
        print('Gcodes to Run:', self.__Gcodes_to_run)

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
        elif status == 'Half':
            self.append_gcode('M106 S127')
        elif status == 'OFF':
            self.append_gcode('M107')

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

    def set_hotend_temp(self, value):
        if value+self.extruder_temp['point'] > 0:
            # +self.extruder_temp['point']))
            self.append_gcode(gcode='M104 S%d' % value)
        else:
            self.append_gcode(gcode='M104 S0')

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
                self.machine_settings['bedleveling_Z_ofsset'], self.machine_settings['bedleveling_Z_move_feedrate'])
            self.append_gcode(gcode=gcode)
            self.append_gcode(gcode='G90')
            gcode = 'G1 X%d Y%d F%f' % (
                self.machine_settings['bedleveling_X1'], self.machine_settings['bedleveling_Y1'], self.machine_settings['traveling_feedrate'])
            self.append_gcode(gcode=gcode)
            self.append_gcode(gcode='G1 Z0')

        if stage == 2:
            self.append_gcode(gcode='G91')
            gcode = 'G1 Z%f F%f' % (
                self.machine_settings['bedleveling_Z_ofsset'], self.machine_settings['bedleveling_Z_move_feedrate'])
            self.append_gcode(gcode=gcode)
            self.append_gcode(gcode='G90')
            gcode = 'G1 X%d Y%d F%f' % (
                self.machine_settings['bedleveling_X2'], self.machine_settings['bedleveling_Y1'], self.machine_settings['traveling_feedrate'])
            self.append_gcode(gcode=gcode)
            self.append_gcode(gcode='G1 Z0')

        if stage == 3:
            self.append_gcode(gcode='G91')
            gcode = 'G1 Z%f F%f' % (
                self.machine_settings['bedleveling_Z_ofsset'], self.machine_settings['bedleveling_Z_move_feedrate'])
            self.append_gcode(gcode=gcode)
            self.append_gcode(gcode='G90')
            gcode = 'G1 X%d Y%d F%f' % (
                self.machine_settings['bedleveling_X1'], self.machine_settings['bedleveling_Y2'], self.machine_settings['traveling_feedrate'])
            self.append_gcode(gcode=gcode)
            self.append_gcode(gcode='G1 Z0')

        if stage == 4:
            self.append_gcode(gcode='G91')
            gcode = 'G1 Z%f F%f' % (
                self.machine_settings['bedleveling_Z_ofsset'], self.machine_settings['bedleveling_Z_move_feedrate'])
            self.append_gcode(gcode=gcode)
            self.append_gcode(gcode='G90')
            gcode = 'G1 X%d Y%d F%f' % (
                self.machine_settings['bedleveling_X2'], self.machine_settings['bedleveling_Y2'], self.machine_settings['traveling_feedrate'])
            self.append_gcode(gcode=gcode)
            self.append_gcode(gcode='G1 Z0')

    def refresh_temp(self):
        self.append_gcode('M105', 1)

    ''' print '''

    def start_printing_thread(self, gcode_dir, line=0):
        print('@@@ printing file dir:', gcode_dir)
        self.time = Time()
        self.printing_file = gcode_dir
        gcode_dir = self.base_path + '/' + gcode_dir
        read_file_gcode_lines_thread = threading.Thread(
            target=self.__read_file_gcode_lines, args=(gcode_dir, line,))
        if self.use_ext_board:
            self.ext_board.flush_input_buffer()
            self.ext_board.off_A_flag()
        read_file_gcode_lines_thread.start()
        print ('started')

    def stop_printing(self):
        self.__stop_flag = True
        self.on_the_print_page = False

    def pause_printing(self):
        self.__pause_flag = True

    def resume_printing(self):
        self.__pause_flag = False
        self.__filament_pause_flag = False
        self.ext_board.flush_input_buffer()
        self.ext_board.off_A_flag()

    def get_percentage(self):
        return self.print_percentage

    """ Feedrate means changes speed on X, Y,Z and E axis """

    def set_feedrate_speed(self, percentage):
        #self.__Feedrate_speed_percentage = percentage
        self.append_gcode(gcode='M220 S%d' % (percentage))

    """ Flow means changes speed on only E axis """

    def set_flow_speed(self, percentage):
        #self.__Travel_speed_percentage = percentage
        self.append_gcode(gcode='M221 S%d' % (percentage))

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
            print (backup_line)
            backup_print.close()
            backup_print_path.close()
            return True, [backup_file_path, backup_line]
        except:
            return False, None

    def delete_last_print_files(self):
        try:
            os.remove('backup_print.bc')
            os.remove('backup_print_path.bc')
        except:
            print("file not removed !")
            

    def stop_move_up(self):
        self.append_gcode('G91')
        self.append_gcode('G1 Z%f F%f' % (self.machine_settings['pause_Z_offset'],
            self.machine_settings['pause_Z_move_feedrate']))
        self.append_gcode('G90')


    ''' recent activites '''

    def check_last_print(self):
        pass

    def set_relay_ext_board(self, number, state):
        self.__relay_updated = True
        self.__relay_state = [number, state]
        # if self.use_ext_board:
        #     self.ext_board.relay_status(number, state)

    def is_filament(self):
        return self .__filament_pause_flag

    def update_filament_status(self):
        self.__update_filament = True


class Utils():
    # util function to get client ip address

    is_first_time = 0

    @staticmethod
    def get_client_ip_django_only(request):
        return request.META.get('REMOTE_ADDR') or request.META.get('HTTP_X_FORWARDED_FOR', '')

    @staticmethod
    def get_server_ip_django_only(request):
        ip = request.get_host().split(':')[0]
        return '127.0.0.1' if ip == '0.0.0.0' else ip

    @staticmethod
    def get_client_ip(request):
        return request.remote_addr

    @staticmethod
    def get_server_ip(request):
        '''
        Only these are possible!
            'localhost'
            '127.0.0.1'
            '192.168.X.X' -> local device ip from that network
        '''
        const_local = '127.0.0.1'
        ip = request.headers.get('Host')
        return const_local if ip == 'localhost' else ip

    @staticmethod
    def get_ip_list():
        # return ['192.168.0.0', '192.168.0.1']
        time.sleep(1)
        ips = os.popen('sudo hostname -I').read()
        return ips.split()

    @staticmethod
    def wifi_con(un, pw):
        try:
            os.popen('nmcli n on')
            answer = os.popen(
                'nmcli d wifi connect \"{0}\" password \"{1}\"'.format(un, pw)).read()
            if answer.find('successfully'):
                return 'success'
            else:
                raise Exception
        except Exception as e:
            print('error in connecting to wifi:', e)
            return 'failure'

    @staticmethod
    def connect_to_config_file_wifi():
        try:
            config = configparser.ConfigParser()
            config.read('/boot/Q-config.ini')
            if config.get('wifi', 'ssid') != '':
                return Utils.wifi_con(config.get('wifi', 'ssid'), config.get('wifi', 'pass'))
        except Exception as e:
            print('no config file found!: ', e)
            return 'no file '

    @staticmethod
    def wifi_list():
        try:
            # is not always wlp2s0. on raspberry: wlan0
            x = os.popen('sudo iw dev wlan0 scan | grep SSID').read()
            y = [m.split() for m in x.split('\n')]
            res = []
            for item in y[:-2]:
                w = ''
                for i in range(1, len(item)):
                    w += str(item[i])
                    # if i != len(item) - 1:
                    #     w += ' '
                    w += ' ' if i != len(item)-1 else ''
                if w != '':
                    res.append(w)
            return res
        except Exception as e:
            print('ERROR in getting wifi list: ', e)
            return None

    """ directories """
    @staticmethod
    def get_connected_usb():
        """
        select a usb
        :return:
        first is any usb connected or not
        second the exception or the directories of usb
        """
        sub_usb_dir = subprocess.Popen(
            ['ls', BASE_PATH], stdout=subprocess.PIPE).communicate()[0]
        sub_usb_dir = sub_usb_dir[:-1]
        if sub_usb_dir == '':
            return None
            # return False,'No usb found.'
        else:
            sub_usb_dir = sub_usb_dir.split(b'\n')
            sub_usb_dir = [x.decode('utf-8') for x in sub_usb_dir]
            return sub_usb_dir

    @staticmethod
    def get_usb_files(sub_dir):
        """
        :param sub_dir:
        the name if the usb taken from 'get connected usb '
        or the sub foldr name
        :return:
        all founded files and folders names
        """
        sub_dir = BASE_PATH + '/' + sub_dir
        files = os.listdir(sub_dir)
        folders, gcodes = [], []
        for name in files:
            if name.endswith('.gcode'):
                gcodes.append(str(name))
            if os.path.isdir(os.path.join(sub_dir, name)):
                folders.append(str(name))

        for g in gcodes:
            folders.append(g)
        return folders


class Extra():
    def __init__(self):
        self.homed_axis = []

    def addHomeAxis(self, axis):
        if axis != 'All' and axis not in self.homed_axis:
            self.homed_axis.append(axis)
        elif axis == 'All':
            self.homed_axis = ['X', 'Y', 'Z']

    def checkHomeAxisAccess(self):
        if 'X' in self.homed_axis and 'Y' in self.homed_axis and 'Z' in self.homed_axis:
            return True
        return False


class Time:
    """
    Initialize object to start the timer for print 
    use Time.read() to read the elapsed time from the start time 
    at the end use Time.stop() to stop the timer and read the hole time elapsed 
    """

    def __init__(self):
        self.start_time = time.time()

    def restart(self):
        self.start_time = time.time()

    # return value as milliseconds
    def read(self):
        elapsed_time = time.time() - self.start_time
        return int(elapsed_time)

    def stop(self):
        elapsed_time = time.time() - self.start_time
        self.start_time = None
        return int(elapsed_time)


class RaspberryHardwareInfo:  # new
    pass
    # """
    # thanks to this repository
    # https://github.com/gavinlyonsrepo/raspberrypi_tempmon.git
    # """
    # @staticmethod
    # def get_cpu_tempfunc():
    #     """ Return CPU temperature """
    #     result = 0
    #     mypath = "/sys/class/thermal/thermal_zone0/temp"
    #     with open(mypath, 'r') as mytmpfile:
    #         for line in mytmpfile:
    #             result = line
    #
    #     result = float(result)/1000
    #     result = round(result, 1)
    #     return result
    #
    # @staticmethod
    # def get_gpu_tempfunc():
    #     """ Return GPU temperature as a character string"""
    #     res = os.popen('/opt/vc/bin/vcgencmd measure_temp').readline()
    #     return float(res.replace("temp=", ""))
    #
    # @staticmethod
    # def get_cpu_use():
    #     """ Return CPU usage using psutil"""
    #     return psutil.cpu_percent()
    #
    # @staticmethod
    # def get_ram_info():
    #     """ Return RAM usage using psutil """
    #     return psutil.virtual_memory()[2]
    #
    # @staticmethod
    # def get_swap_info():
    #     """ Return swap memory  usage using psutil """
    #     return psutil.swap_memory()[3]


class ExtendedBoard:
    def __init__(self, board_port='/dev/ttyS0', board_baudrate=9600):
        self.filament_exist = True
        self.relay1 = False
        self.relay2 = False
        self.board_port = board_port
        self.board_baudrate = board_baudrate

        self.board_serial = serial.Serial(
            port=self.board_port,
            baudrate=self.board_baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        self.board_serial.close()
        self.board_serial.open()
        time.sleep(2)
        self.board_serial.write(b'S')
        timeout_time = time.time()
        check_number = 0
        while True:

            '''  check for time out time '''
            if time.time() - timeout_time > 0.2:
                self.board_serial.write(b'S')
                timeout_time = time.time()
                check_number += 1

            if check_number > 3:
                print ('!!! extended board not found !!!')
                raise BaseException('!!! no board found !!!')

            if self.board_serial.inWaiting():
                text = str(self.board_serial.readline())
                if text.find('ok') != -1:
                    break

    def check_filament_status(self):
        # pass
        """
        check filament
        is exist return true
        not exist return false and the printer most pause
        if return None it means its in the last situation


        """
        if self.board_serial.inWaiting() > 0:
            text = str(self.board_serial.readline())

            if text.find('A') != -1:
                self.filament_exist = False
                return False

            else:
                self.filament_exist = True
                return True

        else:
            return None

    def relay_status(self, relay_num, status):
        """

        set the relay on or off 
        we have 2 relay 

        after sending the data it will wait for  an 'ok' to recive frome board 



        """
        if relay_num == 1:
            if status:
                self.board_serial.write(b'O')
            else:
                self.board_serial.write(b'P')

        elif relay_num == 2:
            if status:
                self.board_serial.write(b'W')
            else:
                self.board_serial.write(b'E')

        while True:
            text = str(self.board_serial.readline())
            if text.find('ok') != -1:
                return

    def flush_input_buffer(self):
        self.board_serial.flushInput()

    def off_A_flag(self):
        self.board_serial.write(b'M')

    def off_B_flag(self):
        self.board_serial.write(b'N')
