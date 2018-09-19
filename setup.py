import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='quantum3d',
    version='0.2',
    author='imans77',
    author_email='iman.s_sani@yahoo.com',
    description=('''Quantum 3D Printer User Interface'''),
    packages=[
        'quantum3d',
        'tests',
    ],
    include_package_data=True,
    requires=[
        'tests'
    ],
    install_requires=[
        'flask',
        'flask-socketio',
        'python-dotenv',
        'pyserial',
    ],
    long_description=read('README.md'),
    keywords="quantum 3d printer ui",
    url="www.quantum3d.ir",
    license="MIT",
)
