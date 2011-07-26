#!/usr/bin/env python

import os
import re
import hashlib
import datetime

from bottle import run, debug

# The script has to run from the location on disk that it lives.
os.chdir(os.path.dirname(__file__))

from util import config, ENV

activate_this = '/srv/sites/%s/bin/activate_this.py' % ENV
#execfile(activate_this, dict(__file__=activate_this))

import routes

if __name__ == '__main__':
    if ENV in ('dev', 'dev2'):
        debug(True)
    run(server='twisted',
        host=config.get('Settings', 'address'),
        port=config.getint('Settings', 'port'))
