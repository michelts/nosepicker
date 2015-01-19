
import os
import glob
from setuptools import setup, find_packages

VERSION='1.0.2'

setup(
    name = 'nosepicker',
    version = VERSION,
    license = 'PSF',
    keywords = 'nose xunit output parser',
    url = 'http://tuohela.net/packages/nosepicker',
    scripts = glob.glob('bin/*'),
    author = 'Ilkka Tuohela',
    author_email = 'hile@iki.fi',
    description = 'Scripts to parse nose xunit XML output files',
    packages = ['nosepicker'] + ['nosepicker.%s'%s for s in find_packages('nosepicker')],
    install_requires = (
        'lxml',
        'setproctitle',
    ),
)

