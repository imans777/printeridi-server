import os
package = os.environ['FLASK_APP'].strip()
dirname, filename = os.path.dirname(__file__), os.path.basename(__file__)
namespace = '.'.join(dirname[dirname.index(package):].split(os.path.sep))

pyList = os.scandir(dirname)
for item in pyList:
    if item.is_file() and item.name != filename:
        name = item.name.split('.')[0]  # remove extension
        getattr(__import__(namespace, fromlist=[name]), name)
