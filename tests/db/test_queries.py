
from unittest import TestCase
from ddt import ddt, data, unpack

from quantum3d import db as db_file
from quantum3d.db import db
from sqlite3 import Connection, Cursor


@ddt
class DBCreationTest(TestCase):
    def setUp(self):
        # drop tables
        db.cursor.execute('''SELECT name FROM sqlite_master
                            WHERE type='table';''')
        table_names = [name[0] for name in db.cursor.fetchall()]
        for table_name in table_names:
            if table_name != 'sqlite_sequence':
                db.cursor.execute('''DROP TABLE %s;''' % (table_name))

    def test_create_connection(self):
        self.assertTrue(isinstance(db.db, Connection))
        self.assertTrue(isinstance(db.cursor, Cursor))

    @data(['settings', 'Settings'],
          ['extra', 'Extra'],
          ['last_prints', 'Prints']
          )  # add all tables with their corresponding table creation function name here
    @unpack
    def test_create_tables(self, func_name, table_name):
        getattr(db, 'create_%s_table' % func_name)()
        db.cursor.execute('''SELECT name FROM sqlite_master
            WHERE type='table' AND name='%s';''' % (table_name))
        table = db.cursor.fetchone()[0]
        self.assertEqual(table, table_name)

    def test_set_default_settings_1(self):
        db.create_all_tables()
        db.set_default_settings(force=False)
        db.cursor.execute('SELECT * FROM Settings')
        self.assertTrue(db.cursor.fetchone())
        db.cursor.execute('SELECT * FROM Extra')
        self.assertTrue(db.cursor.fetchone())

    def test_set_default_settings_2(self):
        '''
        if a default row already exists, setting default settings
        with force=False should not overwrite new values into it!
        '''
        db.create_all_tables()
        db.cursor.execute("""
            INSERT INTO Settings
            (name, bedleveling_X1, bedleveling_X2,
            bedleveling_Y1, bedleveling_Y2,
            traveling_feedrate, bedleveling_Z_ofsset,
            bedleveling_Z_move_feedrate, hibernate_Z_offset,
            hibernate_Z_move_feedrate, pause_Z_offset,
            pause_Z_move_feedrate, printing_buffer)
            VALUES ('default', -292, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        """)
        db.set_default_settings(force=False)
        db.cursor.execute('SELECT * FROM Settings')
        self.assertEqual(db.cursor.fetchone()[1], -292)

    def test_set_default_settings_3(self):
        '''
        new values should not affect with force=False
        '''
        db.create_all_tables()
        db.cursor.execute("""        
            INSERT INTO Extra(id, ABS, pin)
            VALUES (?, ?, ?)    
        """, (0, 'no', '1234'))
        db.set_default_settings(force=False)
        db.cursor.execute('SELECT * FROM Extra')
        self.assertEqual(db.cursor.fetchone()[2], '1234')

    def test_set_default_settings_with_force_1(self):
        db.create_all_tables()
        db.set_default_settings(force=True)
        db.cursor.execute('SELECT * FROM Settings')
        self.assertTrue(db.cursor.fetchone())
        db.cursor.execute('SELECT * FROM Extra')
        self.assertTrue(db.cursor.fetchone())

    def test_set_default_settings_with_force_2(self):
        '''
        If a default row already exists, setting default settings
        with force=True should overwrite new values onto that row
        '''
        db.create_all_tables()
        db.cursor.execute("""
            INSERT INTO Settings
            (name, bedleveling_X1, bedleveling_X2,
            bedleveling_Y1, bedleveling_Y2,
            traveling_feedrate, bedleveling_Z_ofsset,
            bedleveling_Z_move_feedrate, hibernate_Z_offset,
            hibernate_Z_move_feedrate, pause_Z_offset,
            pause_Z_move_feedrate, printing_buffer)
            VALUES ('default', -292, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        """)
        db.set_default_settings(force=True)
        db.cursor.execute('SELECT * FROM Settings')
        self.assertEqual(db.cursor.fetchone()[1], db.default_settings[1])

    def test_set_default_settings_with_force_3(self):
        '''
        new values should affect with force=True
        '''
        db.create_all_tables()
        db.cursor.execute("""        
            INSERT INTO Extra(id, ABS, pin)
            VALUES (?, ?, ?)    
        """, (0, 'no', '1234'))
        db.set_default_settings(force=True)
        db.cursor.execute('SELECT * FROM Extra')
        self.assertEqual(db.cursor.fetchone()[2], '')


@ddt
class DBQueryTest(TestCase):
    @classmethod
    def setUpClass(self):
        db.create_all_tables()

    def setUp(self):
        db.set_default_settings(force=True)

    def tearDown(self):
        # remove test added settings and prints
        db.cursor.execute(''' DELETE FROM Settings WHERE name <> 'default' ''')
        db.cursor.execute(''' DELETE FROM Prints ''')

    def test_get_settings_1(self):
        s = db.get_settings('default')
        self.assertEqual(s[1], db.default_settings[1])

    def test_get_settings_2(self):
        db.cursor.execute("""
            INSERT INTO Settings
            (name, bedleveling_X1, bedleveling_X2,
            bedleveling_Y1, bedleveling_Y2,
            traveling_feedrate, bedleveling_Z_ofsset,
            bedleveling_Z_move_feedrate, hibernate_Z_offset,
            hibernate_Z_move_feedrate, pause_Z_offset,
            pause_Z_move_feedrate, printing_buffer)
            VALUES ('new', -292, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        """)
        s = db.get_settings('new')
        self.assertEqual(s[1], -292)

    def test_set_settings(self):
        db.set_settings(('new', -292, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        db.cursor.execute('SELECT * FROM Settings WHERE name="new"')
        self.assertTrue(db.cursor.fetchone())

    @data('1234', '0000', '0022', '9340', 6543)
    def test_set_pin(self, pin):
        db.set_pin(pin)
        db.cursor.execute('SELECT pin FROM Extra')
        p = db.cursor.fetchall()
        self.assertEqual(len(p), 1)
        self.assertEqual(p[0][0], str(pin))

    @data('1234', '0000', '0022', '9340')
    def test_get_pin_1(self, pin):
        db.cursor.execute(''' UPDATE Extra SET pin = ? ''', (pin,))
        p = db.get_pin()
        self.assertEqual(pin, p)

    def test_get_pin_2(self):
        self.assertFalse(db.get_pin())

    @data(0, 1)
    def test_set_abs(self, abs):
        db.set_abs(abs)
        db.cursor.execute('SELECT ABS FROM Extra')
        a = db.cursor.fetchall()
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0][0], abs)

    @data(0, 1)
    def test_get_abs(self, abs):
        db.cursor.execute(''' UPDATE Extra SET ABS = ? ''', (abs,))
        a = db.get_abs()
        self.assertEqual(abs, a)

    @data((
        '192083945',
        'Extruder: 180.0 - Bed: 35',
        'File 1',
        'Yes'
    ), (
        '0840534',
        'Extruder: 215 - Bed: 50',
        'File 2',
        'No'
    ))
    def test_add_print_info_1(self, print_info):
        db.add_print_info(print_info)
        db.cursor.execute('''
            SELECT * FROM Prints WHERE file_name = ?
        ''', (print_info[2],))
        self.assertEqual(print_info[2], db.cursor.fetchone()[3])

    @data({
        'time': '19810923123',
        'temperature': 'Extruder: 180.0 - Bed: 35',
        'file_name': 'File 1',
        'is_finished': 'Yes'
    }, {
        'time': '49038204',
        'temperature': 'Extruder: 215 - Bed: 50',
        'file_name': 'File 2',
        'is_finished': 'No'
    })
    def test_add_print_info_2(self, print_info):
        db.add_print_info(dict_info=print_info)
        db.cursor.execute('''
            SELECT * FROM Prints WHERE file_name = ?
        ''', (print_info['file_name'],))
        self.assertEqual(print_info['file_name'], db.cursor.fetchone()[3])

    def test_get_last_prints(self):
        db.cursor.execute('''
            INSERT INTO Prints 
            (time, temperature, file_name, is_finished)
            values
            ('1', '2222', '3', '4444'),
            ('11', '222', '33', '444'),
            ('111', '22', '333', '44'),
            ('1111', '2', '3333', '4')
        ''')
        last_prints = db.get_last_prints(3)
        self.assertEqual(len(last_prints), 3)
        self.assertIn('11', list(map(lambda x: x['time'], last_prints)))
        self.assertIn('111', list(map(lambda x: x['time'], last_prints)))
        self.assertIn('1111', list(map(lambda x: x['time'], last_prints)))
