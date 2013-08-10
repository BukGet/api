#!/usr/bin/env python
from pymongo import MongoClient
from fabric.api import *
from fabric.contrib import *
import os
import gzip
import re
import json
import time
import datetime

class LogParser(object):
    servers = ['dallas.vpn.bukget.org', 'paris.vpn.bukget.org']
    ignores = ['java', 'php', 'mozilla', 'chrome', 'opera', 'wget', 
               'curl', 'urllib', 'bot', 'spider', 'apache']
    ua = re.compile(r'\"[^ ]*\" \"([^\(\/ ]*).*\"$')
    rcode = re.compile(r'HTTP/\d\.\d\" (\d{3})')


    def __init__(self):
        self.conn = MongoClient()
        self.db = self.conn.bukget
        self.webstats = self.db.webstats
        self.plugins = self.db.plugins


    def run(self):
        '''
        Perform all of the needed actions...
        '''
        for server in self.servers:
            self.get_log(server)
        self.parse_logs()
        self.popularity()


    def get_log(self, host):
        '''
        Log Retreival
        '''
        env.warn_only = True
        env.user = 'root'
        env.key_filename = '/etc/bukget/keys/id_rsa'
        date = datetime.datetime.now()
        log = '/var/log/bukget/api-access.log-%s.gz' % date.strftime('%Y%m%d')
        env.host_string = 'root@%s:22' % host
        if not os.path.exists('/tmp/bukgetlogs'):
            os.makedirs('/tmp/bukgetlogs')
        get(log, '/tmp/bukgetlogs/%s.log.gz' % host)


    def ignore_ua(self, line):
        '''
        Checks the User-Agent against anything we wish to ignore.  If there are 
        no matches (i.e. a good UA string) then return the string, otherwise
        return False.
        '''
        ua_string = self.ua.findall(line)
        if len(ua_string) > 0:
            ua_string = ua_string[0]
        else:
            return False
        for ignore in self.ignores:
            if ignore in ua_string:
                return False
        if ua_string == '-':
            return False
        return ua_string.replace('.', '_')


    def check_return_code(self, line, logfile):
        '''
        Checks the return code and looks to see if there are any 500 errors.
        If the entry does contain a 500 error, then prin the line to the screen.
        '''
        show = False
        codes = self.rcode.findall(line)
        for item in codes:
            if item == '500':
                show = True
        if show: print '{%s} %s' % (logfile, line.strip('\n'))



    def parse_logs(self):
        '''
        Log Marsing Function
        '''
        data = {
            'total': 0,
            'api1': 0,
            'api2': 0,
            'api3': 0,
            'unique': 0, 
            'plugins': {},
            'user_agents': {},
            'bukkitdev': 0, 
            'timestamp': int(time.time()),
        }
        ipaddys = {'total': []}
        ipaddy = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        api1 = re.compile(r'plugin/([^/ \?]*)')
        api3 = re.compile(r'plugins/[^/ ]*/([^/ \?]*)')
        plist = [p['slug'] for p in self.plugins.find({})]
        for log in os.listdir('/tmp/bukgetlogs'):
            if log[-2:] != 'gz': continue
            lfile = gzip.open('/tmp/bukgetlogs/%s' % log)
            for line in lfile.readlines():
                # Get the IP Address
                ip = ipaddy.findall(line)[0]
                
                # Now to pull the plugin name from the log.  As this
                # can depend on the API we are calling, we will first
                # look for a match from the api3 regex and fallback to
                # the regex that will find entries for api1 and api2.
                plugin = api3.findall(line)
                if len(plugin) < 1:
                    plugin = api1.findall(line)

                # Next we will check to see if this IP is unique or not.
                # If the IP is unique then we will increment in the unique
                # counter and add the IP to our unique counter.
                data['total'] += 1
                if ip not in ipaddys['total']:
                    ipaddys['total'].append(ip)
                    data['unique'] += 1

                # Next we need to determine what kind of api call this was
                # and increment the appropriate counter.
                if 'GET /1/' in line: data['api1'] += 1
                elif 'GET /2/' in line: data['api2'] += 1
                elif 'GET /3/' in line: data['api3'] += 1

                # This is where we compute the counts for all of the user-agent
                # strings.
                uastring = self.ignore_ua(line)
                if uastring:
                    if uastring.lower() not in data['user_agents']:
                        data['user_agents'][uastring] = 0
                    data['user_agents'][uastring] += 1

                # We should also print out any 500 errors so that cron will
                # email out the resulting output to the admins.
                self.check_return_code(line, log)

                if len(plugin) > 0:
                    p = plugin[0]
                    if 'http://bukget.org/pages/stats.html' in line:
                        continue
                    if p not in plist: continue
                    if p not in data['plugins']:
                        data['plugins'][p] = {'unique': 0, 'total': 0}
                        ipaddys[p] = []
                    if ip not in ipaddys[p]:
                        data['plugins'][p]['unique'] += 1
                        ipaddys[p].append(ip)
                    data['plugins'][p]['total'] += 1
            os.remove('/tmp/bukgetlogs/%s' % log)
        self.webstats.save(data)


    def popularity(self):
        '''
        Popularity Trending
        '''
        day_trend = list(self.db.webstats.find().sort('_id', -1).limit(1))[0]
        week_trend = list(self.db.webstats.find().sort('_id', -1).limit(7))
        month_trend = list(self.db.webstats.find().sort('_id', -1).limit(30))

        for plugin in self.plugins.find({}):
            # First
            if 'popularity' not in plugin:
                plugin['popularity'] = {}

            # Daily Trending
            daily = 0
            if plugin['slug'] in day_trend['plugins']:
                daily = day_trend['plugins'][plugin['slug']]['unique']

            # Weekly Trending
            weekly = 0
            for day in week_trend:
                if plugin['slug'] in day['plugins']:
                    weekly += day['plugins'][plugin['slug']]['unique']

            # Monthly Trending
            monthly = 0
            for day in month_trend:
                if plugin['slug'] in day['plugins']:
                    monthly += day['plugins'][plugin['slug']]['unique']

            # Now to add all of the new values to the plugin...
            plugin['popularity']['daily'] = daily
            plugin['popularity']['weekly'] = weekly / 7
            plugin['popularity']['monthly'] = monthly / 30

            # Lastly save the changes :)
            self.plugins.save(plugin)


if __name__ == '__main__':
    lp = LogParser()
    lp.run()