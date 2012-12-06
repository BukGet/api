import logging

_loglevels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}


log = logging.getLogger('bukget')
hdlr = logging.FileHandler('bukget.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.setLevel(_loglevels['debug'])
log.addHandler(hdlr)