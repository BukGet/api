import time
import threading
import json
import os
import sys
import pymongo
from hashlib import md5
from urllib2 import urlopen, HTTPError, URLError
from BeautifulSoup import BeautifulSoup
from ConfigParser import ConfigParser
import logging

# Lets go ahead and read in the configuration file...
config = ConfigParser()
config.read('/etc/bukget/bukgen.conf')

# The usual boring database connection stuff.  Nothing really worthwhile to
# see here ;)
connection = pymongo.MongoClient(config.get('Settings', 'database_host'), 
                                 config.getint('Settings', 'database_port'))
db = connection.bukget

# This is a dumping ground ofr any JSONs that have failed to be inserted into
# the database.  While this rarely happens, it's nice to be able to see the
# actual data that failed to insert.
if not os.path.exists(config.get('Settings', 'json_dump')):
    os.mkdirs(config.get('Settings', 'json_dump'))


def genlog(name):
    '''Log Generator
    This function simply generates a log instance using a combination of the
    name that was provided and the log information in the configuration file.
    '''
    _loglevels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
    }


    log = logging.getLogger('bukgen:%s' % name)
    hdlr = logging.FileHandler(config.get('Settings', 'log_file'))
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    log.setLevel(_loglevels[config.get('Settings', 'log_level')])
    log.addHandler(hdlr)
    return log


def run(parser, ctype=None):
    '''Runtime Initialization and Execution
    Here is where we actually run a specific parser.  The ctype variable allows
    for us to override the default engine type to perform different tasks.
    '''
    if ctype is None: ctype = sys.argv[1]
    parser.config_type = ctype
    parser.run()


class BaseParser(threading.Thread):
    config_delay = 2
    config_api_host = 'localhost:9123'
    _timer = 0
    
    def _get_page(self, url):
        '''get_page url
        
        Returns a BeautifulSoup object of the HTML page in the URL specified.
        '''
        while (time.time() - self._timer) < self.config_delay:
            time.sleep(0.1)
        self._timer = time.time()
        return BeautifulSoup(self._get_url(url))
    
    
    def _get_url(self, url):
        '''get_url
        
        Return the contents of the URL specified.
        '''
        log.debug('PARSER: Fetching: %s' % url)
        comp = False
        data = ''
        while not comp:
            try:
                data = urlopen(url, timeout=5).read()
                comp = True
            except HTTPError, msg:
                if msg.code == 404:
                    log.error('PARSER: File not found for %s' % url)
                    break
                else:
                    log.warn('PARSER: Connection to "%s" failed, retrying...' % url)
                    time.sleep(self.config_delay)
            except:
                log.warn('PARSER: Connection to "%s" failed, retrying...' % url)
                time.sleep(self.config_delay)
        return data
    
    
    def _hash(self, string):
        '''hash string
        
        Returns a md5sum of the string variable.
        '''
        h = md5()
        h.update(string)
        return h.hexdigest()


    def _api_get(self, filters):
        return db.plugins.find_one(filters)        


    def _add_geninfo(self, data):
        db.geninfo.insert(data)


    def _update_plugin(self, data):
        # --Debugging hackery--
        # This should really be cleaned up.  Eventually this will all be moved
        # into the API when we are just sending post requests to the API to
        # update the information...
        try:
            db.plugins.save(data)
        except:
            del(data['_id'])
            with open('json_dicts/%s.json' % data['slug'], 'w') as jfile:
                jfile.write(json.dumps(data, sort_keys=True, indent=4))
            log.error('PARSER: Could not import %s' % data['slug'])
        