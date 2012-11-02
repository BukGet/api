import time
import threading
from hashlib import md5
from urllib2 import urlopen
from bukget.log import log
from BeautifulSoup import BeautifulSoup

class BaseParser(threading.Thread):
    timer = 0
    delay = 2
    verbose = False
    complete = True

    
    def _get_page(self, url):
        '''get_page url
        
        Returns a BeautifulSoup object of the HTML page in the URL specified.
        '''
        while self.delay_check() < self.delay:
            time.sleep(0.1)
        self.timer = time.time()
        return BeautifulSoup(self._get_url(url))
    
    
    def _get_url(self, url):
        '''get_url
        
        Return the contents of the URL specified.
        '''
        log.debug('Fetching: %s' % url)
        comp = False
        count = 0
        data = ''
        while not comp and count <= 10:
            try:
                count += 1
                data = urlopen(url, timeout=5).read()
                comp = True
            except:
                log.warn('Connection to "%s" failed, retrying...' % url)
                time.sleep(self.delay)
        if count > 5:
            log.error('Could not get %s.' % url)
        return data
    
    
    def _hash(self, string):
        '''hash string
        
        Returns a md5sum of the string variable.
        '''
        h = md5()
        h.update(string)
        return h.hexdigest()


    def delay_check(self):
        '''Returns the number of seconds since the last HTTP request'''
        return (time.time() - self.timer)
        

