
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
