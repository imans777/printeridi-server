
__author__ = "Iman Sahebi <iman.s_sani@yahoo.com>"
__license__ = "The MIT License <http://opensource.org/licenses/MIT>"
__copyright__ = "Copyright (C) 2018 Iman Sahebi - Released under terms of the MIT License"

# Every database related query or calls comes here
import sqlite3
from sqlite3 import Error
from .error_handler import error_handler_with, message

# TODO: NO MORE MOVE SETTINGS TABLE NEEDED! PLEASE REMOVE THEM A.S.A.P!!


class PrinterDB:
    def __init__(self, default_initiate=True):
        import os
        self.connection_count = int(os.environ.get('DB_CONNECTION_LIMIT') or 3)
        self.db = -1
        db_name = os.environ.get('DB_NAME_TEST') if os.environ.get(
            'ENV_MODE') == 'test' else os.environ.get('DB_NAME') or 'database'
        self.create_connection(os.path.join(
            os.path.dirname(__file__),
            '.'.join([db_name, 'db'])
        ))
        self.cursor = -1
        if self.db != -1:
            self.cursor = self.db.cursor()

        # TODO: better to read from file
        self.default_settings = ("default", 50, 180, 50, 180, 3000,
                                 10, 1500, 5, 1500, 10, 1500, 15)

        if default_initiate:
            self.create_all_tables()
            self.set_default_settings()
            print('-> database initialized')

    def create_connection(self, db_address):
        self.connection_count -= 1
        try:
            self.db = sqlite3.connect(
                db_address,
                check_same_thread=False,
                isolation_level=None
            )
            print('-> database connected successfully')
        except Error as e:
            print('ERROR (in database connection) -> ', e)
            if (self.connection_count > 0):
                import time
                time.sleep(1)  # wait for a second
                print('retrying connecting to database...')
                self.create_connection(db_address)
            else:
                print('Maximum db connection limit reached. No database is in use.')

    def create_all_tables(self):
        self.create_settings_table()
        self.create_extra_table()
        self.create_last_prints_table()

    @error_handler_with(message)
    def create_settings_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Settings
            (name TEXT PRIMARY KEY,
            bedleveling_X1 real, bedleveling_X2 real,
            bedleveling_Y1 real, bedleveling_Y2 real,
            traveling_feedrate real, bedleveling_Z_ofsset real,
            bedleveling_Z_move_feedrate real, hibernate_Z_offset real,
            hibernate_Z_move_feedrate real, pause_Z_offset real,
            pause_Z_move_feedrate real, printing_buffer real)
        ''')

    @error_handler_with(message)
    def create_extra_table(self):
        # TODO: this whole table should be removed
        # and should use pickledb for these items!
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Extra
            (id INTEGER PRIMARY KEY CHECK (id = 0),
            ABS INTEGER,
            pin TEXT)
        ''')

    @error_handler_with(message)
    def create_last_prints_table(self):
        # TODO: separate extruder and bed temperature (do it when adding filament_type)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Prints
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            temperature TEXT,
            file_name TEXT,
            is_finished TEXT)
        ''')

    @error_handler_with(message)
    def set_default_settings(self, force=False):
        # force=true only affects the 'default' row in settings table!
        # and it doesn't remove other rows!
        self.cursor.execute("""
            INSERT {} INTO Settings
            (name, bedleveling_X1, bedleveling_X2,
            bedleveling_Y1, bedleveling_Y2,
            traveling_feedrate, bedleveling_Z_ofsset,
            bedleveling_Z_move_feedrate, hibernate_Z_offset,
            hibernate_Z_move_feedrate, pause_Z_offset,
            pause_Z_move_feedrate, printing_buffer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """.format("OR REPLACE" if force else "OR IGNORE"), self.default_settings)

        self.cursor.execute("""
            INSERT {} INTO Extra
            (id, ABS, pin)
            VALUES (?, ?, ?)
        """.format("OR REPLACE" if force else "OR IGNORE"), (0, 1, ''))

    @error_handler_with(message)
    def get_settings(self, name='default'):
        self.cursor.execute('''SELECT * FROM Settings
            WHERE name='%s' ''' % (name))
        settings = self.cursor.fetchone()
        if settings is None:
            # return default settings
            return self.default_settings
        return settings

    @error_handler_with(message)
    def set_settings(self, settings):
        self.cursor.execute("""
                    INSERT INTO Settings
                    (name, bedleveling_X1, bedleveling_X2,
                    bedleveling_Y1, bedleveling_Y2,
                    traveling_feedrate, bedleveling_Z_ofsset,
                    bedleveling_Z_move_feedrate, hibernate_Z_offset,
                    hibernate_Z_move_feedrate, pause_Z_offset,
                    pause_Z_move_feedrate, printing_buffer)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, settings)

    @error_handler_with(message)
    def set_pin(self, pin):
        self.cursor.execute(''' UPDATE Extra SET pin = ? ''', (str(pin),))

    @error_handler_with(message)
    def get_pin(self):
        self.cursor.execute('SELECT pin FROM Extra')
        pin = self.cursor.fetchone()[0]
        if pin is None:
            return None
        # NOTE: be careful that this is string, not int!
        return pin

    @error_handler_with(message)
    def set_abs(self, status):
        self.cursor.execute('UPDATE Extra SET ABS=?', (status,))

    @error_handler_with(message)
    def get_abs(self):
        self.cursor.execute('SELECT ABS FROM Extra')
        return self.cursor.fetchone()[0]

    @error_handler_with(message)
    def get_last_prints(self, limit=10):
        result = []
        self.cursor.execute(''' SELECT * FROM Prints
            ORDER BY id DESC LIMIT ?
        ''', (limit,))
        prints = self.cursor.fetchall()
        for item in prints:
            info = {
                'time': item[1],
                'temperature': item[2],
                'file_name': item[3],
                # 'filament_type': item[4],
                # We don't have filament type yet! So we skip this for now!
                'is_finished': item[4],
            }
            result.append(info)
        return result

    @error_handler_with(message)
    def add_print_info(self, print_info=None, dict_info=None):
        if dict_info:
            print_info = (
                dict_info['time'],
                dict_info['temperature'],
                dict_info['file_name'],
                dict_info['is_finished']
            )
        if print_info:
            self.cursor.execute('''
                INSERT INTO Prints
                (time, temperature, file_name, is_finished)
                VALUES (?, ?, ?, ?)        
            ''', print_info)
