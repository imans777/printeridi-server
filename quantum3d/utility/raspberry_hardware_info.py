import psutil
import os


class RaspberryHardwareInfo:
    """
    thanks to this repository
    https://github.com/gavinlyonsrepo/raspberrypi_tempmon.git
    """
    @staticmethod
    def get_cpu_tempfunc():
        """ Return CPU temperature """
        result = 0
        mypath = "/sys/class/thermal/thermal_zone0/temp"
        with open(mypath, 'r') as mytmpfile:
            for line in mytmpfile:
                result = line

        result = float(result)/1000
        result = round(result, 1)
        return result

    @staticmethod
    def get_gpu_tempfunc():
        """ Return GPU temperature as a character string"""
        res = os.popen('/opt/vc/bin/vcgencmd measure_temp').readline()
        return float(res.replace("temp=", ""))

    @staticmethod
    def get_cpu_use():
        """ Return CPU usage using psutil"""
        return psutil.cpu_percent()

    @staticmethod
    def get_ram_info():
        """ Return RAM usage using psutil """
        return psutil.virtual_memory()[2]

    @staticmethod
    def get_swap_info():
        """ Return swap memory  usage using psutil """
        return psutil.swap_memory()[3]