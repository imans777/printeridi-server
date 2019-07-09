import os
import time
import collections
import codecs


class GCodeParser:
    @staticmethod
    def remove_comment(gcode):
        gcode = gcode.split(';')
        if gcode[0] == '':
            try:
                cura_layer = gcode[1].find('LAYER:')
                if cura_layer == 0:
                    layer = int(gcode[1].split('LAYER:')[1])
                    return 'L%d' % layer

                simplify_layer = gcode[1].find(' layer ')
                if simplify_layer == 0:
                    layer = gcode[1].split(' layer ')[1]
                    layer = int(layer[:layer.find(',')])
                    # layer = gcode[1][8:gcode[1].find(',')]
                    return 'L%d' % layer
            except Exception as e:
                print(" in gcodeparser remove comment %s" % e)
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
