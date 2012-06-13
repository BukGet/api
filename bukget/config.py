from ConfigParser import ConfigParser
import os

config = ConfigParser()
config.read(os.path.join(os.getcwd(), 'bukget.conf'))