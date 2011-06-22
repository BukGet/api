#!/usr/bin/env python
import os
import sys
import getopt
import urllib2
import json
import re
import hashlib
import datetime
import logging
import re
import urllib
import httplib
from logging.handlers import SysLogHandler
from ConfigParser import ConfigParser

#### CONFIGURATION AND PRE-PROCESSING
# The script has to run from the location on disk that it lives.
os.chdir(os.path.dirname(__file__))

# Next we need to load the configuration file into memory.
config = ConfigParser()
config.read(os.path.join(sys.path[0], 'config.ini'))

# Next we need to set the environment flag.
ENV = config.get('Settings', 'environment')

activate_this = '/srv/sites/%s/bin/activate_this.py' % ENV
execfile(activate_this, dict(__file__=activate_this))

# Importing all the various modules we will be needing.
import markdown2
from xenforo import XenForo
from BeautifulSoup import BeautifulSoup    as bsoup
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Table, Column, Integer, String, DateTime, Date, 
                        ForeignKey, Text, Boolean, create_engine, MetaData, 
                        and_, desc)
from sqlalchemy.orm import relationship, backref, sessionmaker
import bottle
from bottle import (route, run, debug, template, request, default_app, 
                    redirect, static_file)

# This is a list of the IP addresses allowed to run the repo generation.
allowed_hosts = config.get('Settings','allowed_hosts').split(',')

# Now we setup the logging
LOG_FORMAT = logging.Formatter('%(name)s: %(levelname)s %(message)s')
SYSLOG = SysLogHandler(address='/dev/log')
SYSLOG.setFormatter(LOG_FORMAT)
log = logging.getLogger('bukget')
log.setLevel(logging.INFO)
log.addHandler(SYSLOG)

# Now we can attach to the database.
engine = create_engine(config.get('Settings', 'db_string'))
Session = sessionmaker(bind=engine)

# Here we declare Base, as it will be used to declaritively define the 
# database with SQLAlchemy.
Base = declarative_base()
#### END CONFIGURATION AND PRE-PROCESSING

class BukkitDB(object):
  host = 'plugins.bukkit.org'
  
  def _post(self, url, payload):
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Content-Length': len(payload),
      'X-Requested-With': 'XMLHttpRequest',
    }
    
    http = httplib.HTTPConnection(self.host)
    http.request('POST', url, body=payload, headers=headers)
    resp = http.getresponse()
    return resp.read()
  
  def get_data(self):
    query_data = {
     'j': 685763,
     'title': '',
     'tag': 'all',
     'author': '',
     'inc_submissions': 'false',
     'pageno': 1
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
  hash        = Column(String(32))
  created     = Column(DateTime)
  
  def __init__(self, plugin, maintainer, email, url):
    self.plugin     = plugin
    self.maintainer = maintainer
    self.email      = email
    self.url        = url
    self.created    = datetime.datetime.now()
  
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
      newd = urllib2.urlopen(self.url).read()
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
    #try:
    api = BukkitDB()
    bktdata = api.get_data()['realdata']
    #except:
    #log.error('Could not contact Bukkit\'s plugin dictionary.')
    #return False
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
    
def get_from_github(filename):
  url = 'https://raw.github.com/SteveMcGrath/bukget/master/docs/%s' % filename
  markdown = markdown2.Markdown()
  raw_file = urllib2.urlopen(url).read()
  return markdown.convert(raw_file)

@route('/add', method='GET')
@route('/add', method='POST')
def add_repo():
  errors = []
  notes = []
  s = Session()
  
  if request.GET.get('hash','').strip():
    # If re received an activation field, then we will need to parse it out
    # and compare it to what we have on file.
    act = request.GET.get('hash','').strip()
    name = request.GET.get('plugin','').strip()
    try:
      repo = s.query(Repository).filter_by(plugin=name).one()
    except:
      errors.append('Activation Failed.  Could not find repository record.')
    else:
      if repo.hash == act:
        repo.activated = True
        s.merge(repo)
        s.commit()
        notes.append('Activation Successful!')
        log.info('%s is now  active and will be cached next generation cycle.' % name)
      else:
        errors.append('Activation Failed.  Activation Hash did not match.')
    
  elif request.POST.get('add','').strip():
    # If the data was posted to the page, then we need to parse out the
    # relevent data, try to match the maintainer to the one that si on the
    # bukkit forums, and lastly send an activation request.
    user = request.POST.get('user','').strip()
    url = request.POST.get('url','').strip()
    email = request.POST.get('email','').strip()
    name = request.POST.get('plugin','').strip()
    
    # Now we need to validate all the data we have to make sure it's ok before
    # continue.  First we will define the regexes that we will use to
    # validate the fields then check to make sure that they get exactly 1
    # response back from each of them.  If we don't, then we need to tell
    # the user what failed and allow them to fix their input.
    remail = re.compile(r'^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,4}$')
    rurl = re.compile(r'^(?:http|https|ftp)\://[a-zA-Z0-9\-\./\?\=\;\%]+')
    ruser = re.compile(r'^[A-Za-z0-9\_\.]+$')
    rname = re.compile(r'^[A-Za-z0-9\_]+$')
    
    if len(remail.findall(email)) <> 1:
      errors.append('Not a Valid Email Address.')
    if len(rurl.findall(url)) <> 1:
      errors.append('Not a Valid URL.')
    if len(ruser.findall(user)) <> 1:
      errors.append('Not a Valid Username')
    if len(rname.findall(name)) <> 1:
      errors.append('Not a Valid Plugin Name')
    if len(s.query(Repository).filter_by(plugin=name).all()) > 0:
      errors.append('Plugin Name Already Exists.')
    
    if len(errors) == 0:
      # If there are no errors, then we will try to activate the repository
      # that was defined.
      new_repo = Repository(name, user, email, url)
      if new_repo.activate():
        notes.append('Please check your Bukkit.org account for ' +\
                     'activation message.  If you havent received one, ' +\
                     'please contact us.')
        s.add(new_repo)
        s.commit()
      else:
        errors.append('We were unable to send your Bukkit.org account the ' +\
                      'activation message.  If this issue continues please '+\
                      'notify us of the issue.')
  s.close()
  return template('page_add', notes=notes, errors=errors)

#@route('/')
#def home_page():
#  return template('page_home')

@route('/')
@route('/news')
def news_page():
  s = Session()
  news = s.query(NewsArticle).order_by(desc(NewsArticle.date)).all()
  return template('page_news', news=news)

@route('/log')
def display_logs():
  logfile = open(config.get('Settings', 'log_file'), 'r')
  logdata = logfile.read()
  logfile.close()
  return template('page_logs', logdata=logdata)

@route('/code')
def github_redirect():
  redirect('https://github.com/SteveMcGrath/bukget')

@route('/about')
def about_us():
  return template('page_about')

@route('/repo.json')
def get_repo_file():
  return static_file('repo.json', config.get('Settings','static_files'))

@route('/help')
def help_page():
  return template('page_markdown', data=get_from_github('help.md'), title='Help')

@route('/plugins')
def search_page():
  return template('page_plugins')

@route('/static/:filename#.+#')
def route_static_files(filename):
  return static_file(filename, root=config.get('Settings', 'static_files'))

@route('/baskit')
def baskit_page():
  return template('page_baskit')

@route('/baskit/download')
def baskit_download():
  redirect('https://raw.github.com/SteveMcGrath/baskit/master/baskit.py')

@route('/generate')
def generate_repository():
  '''
  Generates the master repository file.
  '''
  if request.environ.get('REMOTE_ADDR') in allowed_hosts:
    #log.info('Running Generation Cycle.')
    s = Session()
    rdict = []
    repos = s.query(Repository).filter_by(activated=True).all()
    for repo in repos:
      if repo.update():
        s.merge(repo)
        s.commit()
      if repo.cache is not None:
        rdict.append(json.loads(repo.cache))
    rfile = open(os.path.join(\
                 config.get('Settings', 'static_files'),'repo.json'), 'w')
    rfile.write(json.dumps(rdict))
    rfile.close()
    return '{"plugins": %s}' % len(repos)
  return '{"error": "Not an allowed address"}'

# And here we set everything up for Apache to understand what to do with this
# mess of code ;)
if ENV in ('dev', 'dev2'):
  debug(True)
run(server='twisted', 
    host=config.get('Settings', 'address'), 
    port=config.getint('Settings', 'port'))
