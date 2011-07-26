import os
import datetime
import hashlib
import httplib
import json
import re
import urllib
import urllib2

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Table, Column, Integer, String, DateTime, Date, 
                        ForeignKey, Text, Boolean, create_engine, MetaData, 
                        and_)
from sqlalchemy.orm import relationship, backref, sessionmaker

from util import config, log

# Initialize the database.
engine = create_engine(config.get('Settings', 'db_string'))
Session = sessionmaker(bind=engine)

# All table definitions inherit from this base class.
Base = declarative_base()

class BukkitDB(object):
  host = 'plugins.bukkit.org'
  
  def _post(self, url, payload):
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Content-Length': len(payload),
      'X-I-Am-A-Bot': 'bukget.org',
      'User-Agent': 'bukgetRetriever/woof-woof',
    }
    
    http = httplib.HTTPConnection(self.host)
    http.request('POST', url, body=payload, headers=headers)
    resp = http.getresponse()
    return resp.read()
  
  def get_data(self):
    query_data = {
     'title': '',
     'tag': 'all',
     'author': '',
     'inc_submissions': 'false',
     'pageno': -1 # Retrieve all data when lukegb adds pagination
    }
    form_data = '='
    db = self._post('/data.php?%s' % urllib.urlencode(query_data), form_data)
    return json.loads(db)

class NewsArticle(Base):
  '''
  News article class for the site.
  '''
  __tablename__ = 'news'
  id    = Column(Integer(8), primary_key=True)
  title = Column(String(128))
  date  = Column(DateTime)
  data  = Column(Text)
  
  def __init__(self, title, post, date=None):
    if date is not None:
      self.date = date
    else:
      self.date = datetime.datetime.now()
    self.title = title
    self.data = post
  
  def get_html(self):
    markdown = markdown2.Markdown()
    return markdown.convert(self.data)
NewsArticle.metadata.create_all(engine)

class Repository(Base):
  __tablename__ = 'repository'
  id          = Column(Integer(6), primary_key=True)
  maintainer  = Column(String(32))
  email       = Column(String(128))
  url         = Column(Text)
  plugin      = Column(String(32))
  cache       = Column(Text)
  activated   = Column(Boolean)
  manual      = Column(Boolean)
  hash        = Column(String(32))
  created     = Column(DateTime)
  
  def __init__(self, plugin, maintainer, email, url, manual=False):
    self.plugin     = plugin
    self.maintainer = maintainer
    self.email      = email
    self.url        = url
    self.created    = datetime.datetime.now()
    self.manual     = manual
  
  def _valid(self, d):
    '''
    This function will check to see if the dictionary that we were given is
    valid and usable to import all the information we need.
    '''
    # before we start its worth noting that we will be stepping through all
    # of the definitions that should exist within the json dictionary.  If
    # there are any missing items or malformed items, we should be returning
    # false.  If everything does check out, then True should be returned.
    if 'name' not in d: return False
    if not isinstance(d['name'], unicode): return False
    if 'authors' not in d: return False
    if not isinstance(d['authors'], list): return False
    if 'maintainer' not in d: return False
    if not isinstance(d['maintainer'], unicode): return False
    if 'description' not in d: return False
    if not isinstance(d['description'], unicode): return False
    if 'website' not in d: return False
    if not isinstance(d['website'], unicode): return False
    if 'categories' not in d: return False
    if not isinstance(d['categories'], list): return False
    if 'versions' not in d: return False
    if not isinstance(d['versions'], list): return False
    for v in d['versions']:
      if 'version' not in v: return False
      if not isinstance(v['version'], unicode): return False
      if 'required_dependencies' not in v: return False
      if not isinstance(v['required_dependencies'], list): return False
      if 'optional_dependencies' not in v: return False
      if not isinstance(v['optional_dependencies'], list): return False
      if 'conflicts' not in v: return False
      if not isinstance(v['conflicts'], list): return False
      if 'location' not in v: return False
      if not isinstance(v['location'], unicode): return False
      if 'checksum' not in v: return False
      if not isinstance(v['checksum'], unicode): return False
      if 'branch' not in v: return False
      if not isinstance(v['branch'], unicode): return False
      if 'warn' in v:
        if not isinstance(v['warn'], unicode): return False
      if 'notification' in v:
        if not isinstance(v['notification'], unicode): return False
      if v['branch'] not in ['stable','test','dev']: return False
      for e in v['engines']:
        if 'engine' not in e: return False
        if not isinstance(e['engine'], unicode): return False
        if 'build_min' not in e: return False
        if not isinstance(e['build_min'], int): return False
        if 'build_max' not in e: return False
        if not isinstance(e['build_max'], int): return False
        if not e['build_min'] <= e['build_max']: return False
    
    # If we made it all the way here, then it looks to be a valid dictionary!
    return True
  
  def update(self):
    '''
    Updates the json dictionary cache stored in the database.
    '''
    try:
      request = urllib2.Request(self.url, None, 
                                headers={'User-Agent': 'BukGet/0.0.1'})
      newd = urllib2.urlopen(request).read()
      d = json.loads(newd)
    except:
      log.error('Could not read from %s\'s package.json' % self.plugin)
      return False
    if not self._valid(d):
      log.error('%s\'s remote package.json does not appear to be valid.' % self.plugin)
      return False
    
    # New we are going to compare the newly downloaded data to the one we have
    # in the cache.  if the 2 don't match, then we will update the cache with
    # the newer information.
    cur = hashlib.md5()
    cur.update(str(self.cache))
    new = hashlib.md5()
    new.update(newd)
    if new.hexdigest() != cur.hexdigest():
      self.cache = newd
      log.info('Updated %s\'s local package.json' % self.plugin)
      return True
    else:
      return False
  
  def activate(self):
    '''
    Activates the repository so that it can be used by the bukget clients.
    '''
    rname = re.compile(r'^(?:\[.+?\]){0,1}\s{0,1}(\w+[^ ])')
    check_ok = False
    
    # First we need to pull the json database from bukkit and parse it into
    # a native dictionary.  If this fails then throw an error and log the
    # problem.
    if self.manual:
      return True
    else:
      try:
        api = BukkitDB()
        bktdata = api.get_data()['realdata']
      except:
        log.error('Could not contact Bukkit\'s plugin dictionary.')
        return False
      for plugin in bktdata:
        name = rname.findall(plugin['title'])
        if isinstance(name, list):
          if len(name) > 0:
            if name[0].lower() == self.plugin.lower():
              if plugin['author'].lower() == self.maintainer.lower():
                check_ok = True
                log.info('Matched %s to %s on Bukkit.org' %\
                         (self.maintainer, self.plugin))
      if not check_ok:
        log.info('Unable to match %s to %s on Bukkit.org' %\
                 (self.maintainer, self.plugin))
      else:
        forum = XenForo(config.get('Forum', 'username'), 
                        config.get('Forum', 'password'),
                        config.get('Forum', 'hostname'))
        if forum.login():
          md5 = hashlib.md5()
          md5.update(self.plugin + datetime.datetime.now().ctime())
          self.hash = md5.hexdigest()
          forum.private_message(self.maintainer,
                                'BukGet Plugin Repo Activation',
                                template('bukkit_activation', 
                                         user=self.maintainer,
                                         plugin=self.plugin, 
                                         hash=self.hash), 
                                locked=True)
        return True
      return False
Repository.metadata.create_all(engine)
