#!/usr/bin/env python
from zipfile import ZipFile
from urllib2 import urlopen
from urllib import urlencode
from httplib import HTTPConnection
from StrionIO import StringIO
import json
import cmd


loc = 'plugins'

class BukGet(object):
    host = 'api.bukget.org'
    
    def _request(self, method, url, payload={}, headers={}):
        http = HTTPConnection(self.host)
        body = urlencode(payload)
        
        if method == 'POST':
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            headers['Content-Length'] = len(body)
            http.request('POST', url, body=body, headers=headers)
        else:
            http.request('GET', url, headers=headers)
        resp = http.getresponse()
        try:
            jdata = json.loads(resp.read())
        except:
            jdata = None
        return jdata
    
    def plugin_list(self):
        return self._request('GET', '/api/plugins')
    
    def plugin(self, name):
        return self._request('GET', '/api/plugin/%s' % name)
    
    def categories(self):
        return self._request('GET', '/api/categories')
    
    def plugin_has_update(self, name, version):
        data = self.plugin(name)
        newer = []
        current = None
        
        # First lets find the version installed
        for ver in data['versions']:
            if ver['name'] == version:
                current = ver
        
        # Then lets look for newer versions and if we find any, then add them
        # to the newer list.
        for ver in data['versions']:
            if ver['date'] > current['date']:
                newer.append(ver)
        return newer
    
    def search(self, name, action, value):
        return self._request('POST', '/api/search', payload={'name': name,
                                                             'action': action,
                                                             'value': value})
    
    def download(self, name, version):
        data = self._request('GET', '/api/plugin/%s/%s' % (name, version))
        if data is not None:
            dl_link = data['versions'][0]['dl_link']
            file_data = urlopen(dl_link).read()
            return {
                'name': data['versions'][0]['name'],
                'contents': file_data
                   }
        else:
            return None

class CLI(cmd.Cmd):
    prompt = 'bukget> '
    plugins = {}
    bukget = BukGet()
    
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.read_conf()
    
    def read_conf(self):
        self.plugins = json.load('plugins.json')
    
    def write_conf(self):
        whith open('plugins.json') as jfile:
            json.dump(self.plugins, jfile)
    
    def install(self, bundle):
        if bundle is not None:
            pass
    
    def do_list(self, s):
        '''list
        Lists the installaed plugins
        '''
        for plugin in self.plugins:
            print '%s\t%s\t%s' % (plugin, 
                                  self.plugins[plugin]['version'],
                                  self.plugins[plugin]['type'])
    
    def do_update(self, s):
        '''update [name]
        Updates a specified plugin to the current version.
        '''
        self.install(self.bukget.download(s, 'latest'))
                