from ConfigParser import ConfigParser
import os

config = ConfigParser()
#config.read(os.path.join(os.getcwd(), 'bukget.conf'))
config.read(os.path.join('etc', 'bukget.conf'))