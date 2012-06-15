import logging
from bukget.config import config

_loglevels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}

log = logging.getLogger('bukget')
hdlr = logging.FileHandler(config.get('Settings', 'log_file'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.setLevel(_loglevels[config.get('Settings', 'log_level')])
log.addHandler(hdlr)