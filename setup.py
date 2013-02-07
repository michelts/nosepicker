
import os,glob
from setuptools import setup,find_packages

VERSION='1.0'
README = open(os.path.join(os.path.dirname(__file__),'README.md'),'r').read()

setup(
    name = 'nosepicker',
    version = VERSION,
    license = 'PSF',
    keywords = 'nose xunit output parser',
    url = 'http://tuohela.net/packages/nosepicker',
    zip_safe = False,
    install_requires = ['systematic',],
    scripts = glob.glob('bin/*'),
    packages = ['nosepicker'] + ['nosepicker.%s'%s for s in find_packages('nosepicker')],
    author = 'Ilkka Tuohela',
    author_email = 'hile@iki.fi',
    description = 'Scripts to parse nose xunit XML output files',
    long_description = README,
)

