import time
import serial


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
                raise BaseException('!!! no board found !!!')

            if self.board_serial.inWaiting():
                text = str(self.board_serial.readline())
                if text.find('ok') != -1:
                    break

    def check_filament_status(self):
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
