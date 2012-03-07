import logging

log = logging.getLogger('bukget')
hdlr = logging.FileHandler('bukget.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)