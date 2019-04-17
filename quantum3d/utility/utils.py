import os
import zipfile
import configparser
import time
import subprocess
import serial
import serial.tools.list_ports
from quantum3d.constants import BASE_PATH, SC_FULL_PATH

const_local = '127.0.0.1'


class Utils():
    ''' Used for reading wifi config from config file '''
    is_first_time = 0

    @staticmethod
    def get_client_ip_django_only(request):
        ''' Returns client ip based on django's 'request' object '''
        return request.META.get('REMOTE_ADDR') or request.META.get('HTTP_X_FORWARDED_FOR', '')

    @staticmethod
    def get_server_ip_django_only(request):
        ''' Returns server ip based on django's 'request' object '''
        ip = request.get_host().split(':')[0]
        return const_local if ip == '0.0.0.0' else ip

    @staticmethod
    def get_client_ip(request):
        ''' Returns client ip based on flask's 'request' object '''
        return request.remote_addr

    @staticmethod
    def get_server_ip(request):
        '''
        Returns server ip based on flask's 'request' object
        Technically, only these are possible:
            'localhost'
            '127.0.0.1'
            '0.0.0.0'
            '192.168.X.X' -> local device ip from that network
        '''
        ip = request.headers.get('Host')
        return const_local if (ip == 'localhost' or ip == '0.0.0.0') else ip

    @staticmethod
    def get_ip_list():
        ''' Returns all the IPs that the device already has 
            e.g. ['192.168.0.0', '192.168.0.1'] '''
        try:
            time.sleep(1)
            if os.environ.get('CUR_ENV', 'rpi') == 'win':
                raise Exception('OS_NOT_SUPPORTED')

            ips = os.popen('sudo hostname -I').read()
            return ips.split()
        except Exception as e:
            print('Error (in getting IP list. Maybe not on linux-based system?) -> ', e)
            return []

    @staticmethod
    def wifi_con(un, pw):
        ''' Connects to the wifi thanks to nmcli command '''
        try:
            os.popen('nmcli n on')
            answer = os.popen(
                'nmcli d wifi connect \"{0}\" password \"{1}\"'.format(un, pw)).read()
            if answer.find('successfully'):
                return 'success'
            else:
                raise Exception
        except Exception as e:
            print('Error (in connecting to wifi) -> ', e)
            return 'failure'

    @staticmethod
    def connect_to_config_file_wifi():
        ''' Connects to wifi if there existed a config file '''
        try:
            config = configparser.ConfigParser()
            config.read('/boot/Q-config.ini')
            if config.get('wifi', 'ssid') != '':
                return Utils.wifi_con(config.get('wifi', 'ssid'), config.get('wifi', 'pass'))
        except Exception as e:
            print('Error (no config file found) -> ', e)
            return 'no file '

    @staticmethod
    def wifi_list():
        ''' Returns a list of available wifis, if any '''
        try:
            # it's not always wlp2s0. on raspberry: wlan0
            if os.environ.get('CUR_ENV', 'rpi') == 'win':
                raise Exception('OS_NOT_SUPPORTED')

            x = os.popen('sudo iw dev wlan0 scan | grep SSID').read()
            y = [m.split() for m in x.split('\n')]
            res = []
            for item in y[:-2]:
                w = ''
                for i in range(1, len(item)):
                    w += str(item[i])
                    w += ' ' if i != len(item)-1 else ''
                if w != '':
                    res.append(w)
            return res
        except Exception as e:
            print('ERROR (in getting wifi list) -> ', e)
            return []

    @staticmethod
    def get_connected_usb():
        """ Returns a list of mounted USBs, if any """
        sub_usb_dir = subprocess.Popen(
            ['ls', BASE_PATH], stdout=subprocess.PIPE).communicate()[0]
        sub_usb_dir = sub_usb_dir[:-1]
        if sub_usb_dir == '':
            return None

        sub_usb_dir = sub_usb_dir.split(b'\n')
        sub_usb_dir = [x.decode('utf-8') for x in sub_usb_dir]

        # remove falsely-existing usbs! (empty folders that are not cleaned)
        active_usb = []
        for usb in sub_usb_dir:
            try:
                usb_content = os.popen(
                    'ls "' + os.path.join(BASE_PATH, usb) + '"').read()
                if usb_content:
                    active_usb.append(usb)
            except Exception as e:
                print("error in checking active usbs: ", e)
        return active_usb

    @staticmethod
    def get_usb_files(sub_dir):
        """ Returns all folders and 'gcode' files in the received directory """
        sub_dir = os.path.join(BASE_PATH, sub_dir)
        files = os.listdir(sub_dir)
        folders, gcodes = [], []
        for name in files:
            if os.path.isdir(os.path.join(sub_dir, name)):
                folders.append(str(name))
            elif name.endswith('.gcode'):
                gcodes.append(str(name))
        for g in gcodes:
            folders.append(g)
        return folders

    @staticmethod
    def timelapse_list():
        tl_folders = os.listdir(SC_FULL_PATH)
        folders = []
        for name in tl_folders:
            if os.path.isdir(os.path.join(SC_FULL_PATH, name)):
                folders.append(str(name))
        return folders

    @staticmethod
    def export_timelapse_to_usb(dir_name, usb_name):
        try:
            zipname = dir_name + '.zip'
            zipf = zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED)

            images = os.listdir(os.path.join(SC_FULL_PATH, dir_name))
            for image in images:
                zipf.write(os.path.join(
                    SC_FULL_PATH,
                    dir_name,
                    image
                ), arcname=os.path.join(dir_name, image))
            zipf.close()

            os.popen('cp "{}" "{}"'.format(zipname, os.path.join(
                BASE_PATH,
                usb_name
            )))
            os.popen('rm "{}"'.format(zipname))
            return True
        except Exception as e:
            print("error exporting timelapse: ", e)
            return False

    @staticmethod
    def remove_timelapse_folder(dir_name):
        try:
            os.popen('rm "{}" -r'.format(os.path.join(SC_FULL_PATH, dir_name)))
            return True
        except Exception as e:
            print("error removing timelapse folder: ", e)
            return False

    @staticmethod
    def autofind_printer_serial_port():
        try:
            ports = [tuple(p)
                     for p in list(serial.tools.list_ports.comports())][0]
            return ports[0]
        except:
            return None
