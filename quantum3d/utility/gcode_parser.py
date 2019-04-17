import os
import time
import collections
import codecs


class GCodeParser:
    @staticmethod
    def remove_comment(gcode):
        gcode = gcode.split(';')
        if gcode[0] == '':

            cura_layer = gcode.find(';LAYER:')
            if cura_layer == 0:
                layer = gcode[7:]
                return 'L%d'%layer

            simplify_layer = lines[x].find('; layer')
            if simplify_layer == 0:
                layer = lines[x][8:lines[x].find(',')]
                return 'L%d'%layer

            return None
        else:
            return gcode[0]

    @staticmethod
    def remove_chomp(gcode):
        return gcode.strip()

    @staticmethod
    def parse(gcode):
        gcode = gcode.split(' ')
        dic = collections.OrderedDict()
        for item in gcode:
            if item != '':
                dic['%s' % item[0:1]] = str(item[1:])
        return dic

    @staticmethod
    def rebuild_gcode(dic):
        gcode = ''
        for item in dic:
            gcode += (item + dic[item]) + ' '
        return gcode
