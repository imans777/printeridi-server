import os
import time
import collections

import codecs



class Parser:

    
    @staticmethod
    def remove_comment(gcode):
        gcode = gcode.split(';')
        if gcode[0] == '':
            return None
        else:
            return gcode[0]


    @staticmethod
    def remove_chomp(gcode):
        return gcode.rstrip()


    @staticmethod
    def parse(gcode):
        gcode = gcode.split(' ')
        dic = collections.OrderedDict()
        for item in gcode:
            if item != '':
                dic['%s'%item[0:1]] = str(item[1:])
        return dic


    @staticmethod
    def rebuild_gcode(dic):
        gcode = ''
        for item in dic:
            gcode += ( item + dic[item] ) + ' '
        return gcode


