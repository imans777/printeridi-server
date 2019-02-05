
__author__ = "Iman Sahebi <iman.s_sani@yahoo.com>"
__license__ = "The MIT License <http://opensource.org/licenses/MIT>"
__copyright__ = "Copyright (C) 2018 Iman Sahebi - Released under terms of the MIT License"

import os
RESERVED_NAMES = ['consts']
try:
    package = os.environ['FLASK_APP'].strip()
except:
    print('Could not read FLASK_APP env var!')
    package = 'quantum3d'
dirname, filename = os.path.dirname(__file__), os.path.basename(__file__)
namespace = '.'.join(dirname[dirname.index(package):].split(os.path.sep))

errCnt = 0
pyList = os.scandir(dirname)
for item in pyList:
    try:
        if item.is_file() and item.name != filename:
            name = item.name.split('.')[0]  # remove extension

            if name in RESERVED_NAMES:
                continue

            getattr(__import__(namespace, fromlist=[name]), name)
    except Exception as e:
        print("error importing API route file: ", e)
        errCnt += 1

if errCnt:
    print('''ERROR in module importings ({}) App might not work correctly'''.format(errCnt))
