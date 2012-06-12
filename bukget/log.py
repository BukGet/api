import logging
import bukget.config

log = logging.getLogger('bukget')
hdlr = logging.FileHandler(bukget.config.get('Settings', 'log_file'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.setLevel(bukget.config.getint('Settings', 'log_level'))
log.addHandler(hdlr)