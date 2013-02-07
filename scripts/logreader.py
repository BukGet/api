#!/usr/bin/env python
from pymongo import MongoClient
import gzip
import re
import json
import time
import datetime

conn = MongoClient()
db = conn.bukget
webstats = db.webstats
plugins = db.plugins

log_base = '/var/log/bukget/api-access.log'
date = datetime.datetime.now() - datetime.timedelta(days=1)
log = '%s-%s.gz' % (log_base, date.strftime('%Y%m%d'))

data = {'total': 0, 'unique': 0, 'plugins': {}, 'timestamp': int(time.time())}
lfile = gzip.open(log)

ipaddys = {'total': []}
ipaddy = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
api1 = re.compile(r'plugin/([^/ ]*)')
#api2 = re.compile(r'bukkit/plugin/([^/ ]*)')
api3 = re.compile(r'plugins/[^/ *]*/([^/ ]*)')

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

    if len(plugin) > 0:
        p = plugin[0]
        if p not in data['plugins']:
            data['plugins'][p] = {'unique': 0, 'total': 0}
            ipaddys[p] = []
        if ip not in ipaddys[p]:
            data['plugins'][p]['unique'] += 1
            ipaddys[p].append(ip)
        data['plugins'][p]['total'] += 1
lfile.close()
webstats.save(data)


for plugin in plugins.find({}):
    if 'popularity' not in plugin:
        plugin['popularity'] = {}
    if plugin['slug'] in data['plugins']:
        plugin['popularity']['daily'] = data['plugins'][plugin['slug']]['unique']
    else:
        plugin['popularity']['daily'] = 0
    plugins.save(plugin)