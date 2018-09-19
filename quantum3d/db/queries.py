# Every database related query or calls comes here
import sqlite3
from sqlite3 import Error
from .error_handler import error_handler_with, message


class PrinterDB:
    def __init__(self):
        import os
        self.connection_count = int(os.environ.get('DB_CONNECTION_LIMIT')) or 3
        self.db = -1
        self.create_connection(os.path.join(
            os.getcwd(),
            'database.db'
        ))
        if self.db != -1:
            self.db = self.db.cursor()

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

    @error_handler_with(message)
    def create_settings_table(self):
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS Settings
            (bedleveling_X1 real, bedleveling_X2 real,
            bedleveling_Y1 real, bedleveling_Y2 real,
            traveling_feedrate real, bedleveling_Z_ofsset real,
            bedleveling_Z_move_feedrate real, hibernate_Z_offset real,
            hibernate_Z_move_feedrate real, pause_Z_offset real,
            pause_Z_move_feedrate real, printing_buffer real,
            ABS TEXT, pin real)
        ''')

    @error_handler_with(message)
    def create_last_prints_table(self):
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS Prints
            (time TEXT, temperature TEXT, file_name TEXT, is_finished TEXT)
        ''')

    @error_handler_with(message)
    def get_settings(self):
        self.db.execute('SELECT * FROM Settings LIMIT 1')
        settings = self.db.fetchone()
        if settings is None:
            settings = (50, 180, 50, 180, 3000, 10, 1500,
                        5, 1500, 10, 1500, 15, "yes", None,)
        return settings

    @error_handler_with(message)
    def set_settings(self, settings):
        # TODO: add name to be able to create custom profile for every settings
        self.db.execute("""
                    INSERT INTO Settings
                    (bedleveling_X1, bedleveling_X2,
                    bedleveling_Y1, bedleveling_Y2,
                    traveling_feedrate, bedleveling_Z_ofsset,
                    bedleveling_Z_move_feedrate, hibernate_Z_offset,
                    hibernate_Z_move_feedrate, pause_Z_offset,
                    pause_Z_move_feedrate, printing_buffer, ABS, pin)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, settings)

    @error_handler_with(message)
    def set_pin(self, pin):
        self.db.execute('UDPATE Settings SET pin = ?', (pin,))

    @error_handler_with(message)
    def fetch_pin(self):
        self.db.execute('SELECT pin FROM Settings LIMIT 1')
        pin = self.db.fetchone()[0]
        if pin is None:
            return None
        return int(pin)

    @error_handler_with(message)
    def set_abs(self, status):
        self.db.execute('UPDATE Settings SET ABS=?', (status,))

    @error_handler_with(message)
    def get_abs(self):
        self.db.execute('SELECT ABS FROM Settings LIMIT 1')
        return self.db.fetchone()[0]

    @error_handler_with(message)
    def get_last_prints(self):
        result = []
        self.db.execute('SELECT * FROM Prints LIMIT 10')
        prints = self.db.fetchall()
        for item in prints:
            info = {
                'time': item[0],
                'temperature': item[1],
                'file_name': item[2],
                # 'filament_type': item[3],
                # We don't have filament type yet! So we skip this for now!
                'is_finished': item[3],
            }
            result.append(info)
        return result

    @error_handler_with(message)
    def add_print_info(self, print_info):
        self.db.execute('''
            INSERT INTO Prints VALUES
            (?, ?, ?, ?)        
        ''', print_info)
