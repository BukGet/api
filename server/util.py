import os
import sys
import logging
from logging.handlers import SysLogHandler
from ConfigParser import ConfigParser

# Load the configuration file into memory.
config = ConfigParser()
config.read(os.path.join(sys.path[0], 'config.ini'))

# Set the environment flag.
ENV = config.get('Settings', 'environment')

# List of the IP addresses allowed to run the repo generation.
allowed_hosts = config.get('Settings','allowed_hosts').split(',')

# Now we setup the logging
LOG_FORMAT = logging.Formatter('%(name)s: %(levelname)s %(message)s')
SYSLOG = SysLogHandler(address='/dev/log')
SYSLOG.setFormatter(LOG_FORMAT)
log = logging.getLogger('bukget_%s' % ENV)
log.setLevel(logging.INFO)
log.addHandler(SYSLOG)
