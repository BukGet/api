import time
import threading
import json
import os
from hashlib import md5
from urllib2 import urlopen
from bukget.log import log
from BeautifulSoup import BeautifulSoup

# All of this is debugging hackery
# --HACKERY
from pymongo import MongoClient
connection = MongoClient('localhost', 27017)
db = connection.bukget
try:
    db.plugins.drop()
except:
    pass
if not os.path.exists('json_dicts'):
    os.mkdir('json_dicts')
# --HACKERY

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
        count = 0
        data = ''
        while not comp and count <= 10:
            try:
                count += 1
                data = urlopen(url, timeout=5).read()
                comp = True
            except:
                log.warn('PARSER: Connection to "%s" failed, retrying...' % url)
                time.sleep(self.config_delay)
        if count > 5:
            log.error('PARSER: Could not get %s.' % url)
        return data
    
    
    def _hash(self, string):
        '''hash string
        
        Returns a md5sum of the string variable.
        '''
        h = md5()
        h.update(string)
        return h.hexdigest()


    def _api_get(self, obj, filters):
        return None


    def _add_geninfo(self, data):
        db.geninfo.insert(data)


    def _update_plugin(self, data):
        # Debugging hackery
        with open('json_dicts/%s.json' % data['slug'], 'w') as jfile:
            jfile.write(json.dumps(data, sort_keys=True, indent=4))
        print db.plugins.insert(data)
        