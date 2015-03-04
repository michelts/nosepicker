
import glob
from setuptools import setup, find_packages

VERSION='1.0.3'

setup(
    name = 'nosepicker',
    version = VERSION,
    license = 'PSF',
    keywords = 'nose xunit output parser',
    url = 'https://github.com/hile/nosepicker',
    author = 'Ilkka Tuohela',
    author_email = 'hile@iki.fi',
    description = 'Scripts to parse nose xunit XML output files',
    scripts = glob.glob('bin/*'),
    packages = find_packages(),
    install_requires = (
        'lxml',
        'setproctitle',
    ),
)

