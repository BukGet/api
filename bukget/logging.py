import config
import datetime

def log(msg):
  logfile = open(config.get('Paths', 'logfile'), 'a')
  logfile.write(msg + '\n')
  logfile.close()