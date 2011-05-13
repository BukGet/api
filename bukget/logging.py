import config
import datetime

def log(msg):
  logfile = open(config.get('Paths', 'logfile'), 'a')
  logfile.write('%s: %s\n' % (datetime.datetime.now().ctime(), msg)
  logfile.close()