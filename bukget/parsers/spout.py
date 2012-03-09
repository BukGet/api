import time
import yaml
import json
import re
from StringIO import StringIO
from zipfile import ZipFile
from bukget.parsers.common import BaseParser
from bukget.orm import *

class Parser(BaseParser):
    complete = False
    base_uri = 'http://forums.spout.org'    
    gen_id = 0
    
    def run(self, gen_id):
        self.get_id = gen_id
        #self._forum_parser()
        self.complete = True
    
    def _forum_parser(self):
        curl = 'http://forums.spout.org/view/releases.7/'
        active = True
        while active:
            page = self._get_page(curl)
            for item in page.findAll('a', {'class': 'PreviewTooltip'}):
                self._parse_thread(item.get('href'))
            nurl = page.findAll('a', {'rel': 'next'})
            if len(nurl) > 0:
                curl = '%s/%s' % (self.base_uri, nurl.get('href'))
    
    def _parse_thread(self, url):
        uri = '%s/%s' % (self.base_uri, url)
        page = self._get_page(uri)
        title = page.find('div', {'class': 'titleBar'}).findChild('a').text
        