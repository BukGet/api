import logging
from bukget.config import config

log = logging.getLogger('bukget')
hdlr = logging.FileHandler(config.get('Settings', 'log_file'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.setLevel(config.getint('Settings', 'log_level'))
log.addHandler(hdlr)