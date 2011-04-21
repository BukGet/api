#!/usr/bin/env python

import zipfile
import os
import json
import sys
import time
import shutil
import hashlib
import datetime
import pyclamd
import ConfigParser
import httplib
import urllib2
from BeautifulSoup              import BeautifulSoup as bsoup
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy                 import Table, Column, Integer, String, \
                                       DateTime, Date, ForeignKey, Text, \
                                       Boolean, create_engine, MetaData, and_
from sqlalchemy.orm             import relation, backref, sessionmaker


def _config(stanza, option, opt_type='string'):
  '''
  Open the configuration file and pull the value fromt he stanza and option
  specified.  Optionally the option type can be overriden with opt_type to
  return any of the following types: string, bool, float, and int.
  '''
  config = ConfigParser.ConfigParser()
  config.read('config.ini')
  if opt_type == 'string':
    return config.get(stanza, option)
  if opt_type == 'int':
    return config.getint(stanza, option)
  if opt_type == 'bool':
    return config.getboolean(stanza, option)
  if opt_type == 'float':
    return config.getfloat(stanza, option)
  if opt_type == 'path':
    return os.path.normpath(config.get(stanza, option))

# Open the port to the Clamd daemon.  this will be needed to scan the
# packages as they are initialized to make sure that therte arent any viruses
# in the packages.
pyclamd.init_network_socket(_config('Settings', 'clamd_host'), 
                            _config('Settings', 'clamd_port', 'int'))

sql_string    = _config('Settings', 'database')
engine        = create_engine(sql_string)
Session       = sessionmaker(bind=engine)
Base          = declarative_base()

def get_session():
  session       = Session()
  return session

class UserAPI(Base):
  '''
  This is the class supporting the user API keys that are stored in the
  database.  This class will also handle requesting a new key for a user as
  well.
  '''
  __tablename__ = 'users'
  api           = Column(String(255), primary_key=True)
  username      = Column(String(255), primary_key=True)
  email         = Column(String(255))
  activated     = Column(Boolean)
  
  def __init__(self, name, email):
    self.username   = name
    self.email      = email
    md5             = hashlib.md5()
    md5.update(name + email + datetime.datetime.now().ctime())
    self.api        = md5.hexdigest()
    self.activated  = False
    
class BukGetPkg(Base):
  '''
  This is the generic bukget package object.  Everything from verification,
  addition into the repository, and dumping individual bukget-compliant
  dictionaries are handled within this object.
  '''
  __tablename__ = 'packages'
  dictionary    = None
  status        = None
  valid         = None
  _base         = None
  _repo         = None
  filename      = None
  new_filename  = None
  _engine       = None
  _session      = None
  name          = Column(String(64), primary_key=True)
  version       = Column(String(15), primary_key=True)
  branch        = Column(String(10))
  pkg_type      = Column(String(10))
  author        = Column(String(255))
  description   = Column(Text)
  website       = Column(String(255))
  location      = Column(String(255))
  checksum      = Column(String(255))
  categories    = Column(Text)
  bukkit_min    = Column(Integer)
  bukkit_max    = Column(Integer)
  required_deps = Column(Text)
  optional_deps = Column(Text)
  
  def get_deps(self):
    '''
    Returns the dependency dictionary.
    '''
    return {
      'required': self.required_deps.split(','),
      'optional': self.optional_deps.split(','),
    }
  
  def get_cats(self):
    '''
    Returns the category list.
    '''
    return self.categories.split(',')

  def set_deps(self, values):
    '''
    Reformats the dependency dictionary to be included in the database.
    '''
    self.required_deps  = ','.join(values['required'])
    self.optional_deps  = ','.join(values['optional'])
  
  def set_cats(self, values):
    '''
    Reformats the category list to be included int he database.
    '''
    self.categories     = ','.join(values)
  
  def __init__(self, filename):
    '''
    Initialize and validate the package that has been 
    '''
    
    # First thing we need to pull in the information we need from the config
    # file and set the filename to be persistant in the object.
    self._base          = _config('Settings', 'urlbase')
    self._repo          = _config('Settings', 'repository', 'path')
    self.filename       = os.path.join(_config('Settings', 'uploads'), filename)
    
    # Next we will perform a quick scan of the zipfile to make sure that it
    # is clean of any malware that we are able to detect.
    avstatus            = pyclamd.scan_file(self.filename)
    if avstatus is not None:
      self.valid        = False
      self.status       = 'ClamAV: %s' % avstatus
      return
    
    # Now we want to make sure that the file is really a zipfile. Otherwise
    # there is no point on trying to continue.
    if not zipfile.is_zipfile(self.filename):
      self.valid        = False
      self.status       = 'Not a Zip File'
      return
    
    # Lets go ahead and generate a ZipFile object with the package file so
    # we can start parsing. :)
    package             = zipfile.ZipFile(self.filename, 'a')
    
    # Next we need to make sure that there is at leats a basic structure in
    # the package and that there is at least 1 jar file in the package in
    # order for this to be a valid package.
    checks = 0
    for fname in package.filelist:
      if fname.filename[:3] in ['bin', 'etc', 'lib']:
        checks += 1
      if fname.filename == 'info.json' or fname.filename[-3:] == 'jar':
        checks += 1
    if checks < 5:
      self.valid        = False
      self.status       = 'Not in a Valid Package Format'
      return
    
    # And now we will start to import the info.json file into the object so
    # that we can start using the information later on if we want to add the
    # package to the repository
    self.dictionary     = json.loads(package.read('info.json'))
    try:
      self.name         = self.dictionary['name']
      self.author       = self.dictionary['author']
      self.website      = self.dictionary['website']
      self.version      = self.dictionary['version']
      self.pkg_type     = self.dictionary['pkg_type']
      self.branch       = self.dictionary['branch']
      self.bukkit_min   = int(self.dictionary['bukkit_min'])
      self.bukkit_max   = int(self.dictionary['bukkit_max'])
      papi              = self.dictionary['api']
      self.set_deps(self.dictionary['dependencies'])
      self.set_cats(self.dictionary['categories'])
    except:
      # If we end up here, there must have been an issue with the info.json
      # dictionary and we cannot properly import the package.
      self.valid        = False
      self.status       = 'Malformed information dictionary.'
      return
    
    # Now we need to make sure that the API key that is in the package is
    # both valid and tied to the author.  If it passes we will need to remove
    # it from the dictionary.
    session             = get_session()
    user              = session.query(UserAPI).filter_by(api = papi).first()
    session.close()
    if user.username != self.author:
      self.valid      = False
      self.status     = 'Invalid or Missing API Key'
      return
    
    # If we made it this far then the package has to be valid.  We need to
    # mark the object as such and set the status to an appropriate message :D
    self.valid          = True
    self.status         = 'Valid Package.'
  
  def prep(self):
    '''
    This function will prep the package to the repository.  This includes
    adding the information to the database and moving the file into the
    right location.  Some extra prepping will be performed as well, such as
    checksumming the file so that we can compare it later on with the client
    to make sure that we downloaded it properly.
    '''
    
    # Firstly we will need to setup the md5 and time variables so that we can
    # use them in a little bit.
    md5                 = hashlib.md5()
    time                = datetime.datetime.now()
    
    # Before we do anything else, we need to repack the zip file so the the
    # info.json has all the additional information that we may need.
    tmpfile             = '%s-tmp'% self.filename
    repack              = zipfile.ZipFile(tmpfile, 'w')
    package             = zipfile.ZipFile(self.filename, 'r')
    for item in package.infolist():
      if item.filename == 'info.json':
        dictionary      = self.dictionary
        del dictionary['api']
        repack.writestr(item, json.dumps(dictionary))
      else:
        repack.writestr(item, package.read(item.filename))
    self.remove()
    shutil.move(tmpfile, self.filename)
    
    # Open the package file and read the whole thing into the md5 object so
    # that we can generate a md5sum that we can use to check against.  Once
    # thats done, set the checksum variable to equal what we got back.
    md5.update(open(self.filename, 'rb').read())
    self.checksum       = md5.hexdigest()
    
    # Now we need to set a filename.  In order to keep the madness to a min,
    # we will be simply using a random 5 character filename based on the md5
    # that we just generated.  If the filename exists, we will simply add the
    # time to the md5 and resum and check.  This will repeat until we get an
    # unallocated name and we will use that.
    self.new_filename            = md5.hexdigest()[:5] + '.zip'
    while os.path.exists(os.path.join(self._repo, 'pkgs', self.new_filename)):
      md5.update(time)
      self.new_filename = md5.hexdigest()[:5] + '.zip'
    
    # Next we simply need to slap the filename on the end of the url base
    # that was derrived from the config file when we initialized the object.
    # this should provide a valid URL to point directly to this package.
    self.location       = self._base + self.new_filename

  def move(self):
      # Finally we will move the file into the proper location.  Because the
      # change has already vbeen commited to the database, if there is an issue
      # here then we will have to remove the entry from the database as well.
      try:
        shutil.move(self.filename, os.path.join(self._repo, 'pkgs', 
                                                self.new_filename))
      except:
        self.status       = 'Package Move Failed.'
        return

      # Yayz the package is now part of the repository!
      self.status         = 'Package Added to repository.'
  
  def remove(self):
    os.remove(self.filename)
  
  def dump(self):
    '''
    Dumps a repository-compliant dictionary for use in generating the 
    repository dictionary.
    '''
    return {
             'name': self.name,
           'author': self.author,
      'description': self.description,
          'website': self.website,
          'version': self.version,
         'pkg_type': self.pkg_type,
         'location': self.location,
         'checksum': self.checksum,
           'branch': self.branch,
       'bukkit_min': self.bukkit_min,
       'bukkit_max': self.bukkit_max,
     'dependencies': self.get_deps(),
       'categories': self.get_cats(),
    }

def generate_bukkit_packages():
  '''
  This function will generate the craftbukkit packages for use in importing
  into the repository.  A package will be generated for each branch that is
  specified.
  '''
  
  # These variables are used to denote how ci is setup with static references
  # the last promoted stable build and the last stable build that was built.
  # if the bukkit team changes how these are used down the road then we can
  # update these and re-release the code with the variables reset.  If this
  # becomes a continuing problem these can always be shited over to the config
  # file.
  burl      = 'http://ci.bukkit.org/job/dev-CraftBukkit'
  artifact  = 'artifact/target/craftbukkit-0.0.1-SNAPSHOT.jar'
  branches  = {
    'stable': '%s/promotion/latest/Recommended' % burl,
      'test': '%s/lastStableBuild' % burl,
       'dev': '%s/lastSuccessfulBuild' % burl,
  }
  
  # For every defined branch, we will create a package.  It is understood
  # that there may be double or even triple work here at times, however at
  # the same time the package addition will knowingly fail in this case, and
  # that is perfectly ok.
  # NOTE: Some of this code is more than likely NOT win32 safe!!!!
  for branch in branches:
     url      = branches[branch]
     zf       = open(os.path.join(_config('Settings', 'uploads', 'path'), 
                                         'craftbukkit-%s.zip' % branch), 'wb')
     zfile    = zipfile.ZipFile(zf, 'w')
     try:
       page   = bsoup(urllib2.urlopen(url).read())
     except:
       return  
     build    = int(page.find(name='title').text.split()[1].strip('#'))
     session  = get_session()
     query    = session.query(UserAPI).filter_by(username = 'Bukkit Team').first()
     api      = query.api
     session.close()

     # Generate file info and download craftbukkit.
     cb                = zipfile.ZipInfo()
     cb.filename       = 'bin/craftbukkit.jar'
     cb.date_time      = time.localtime()[:6]
     cb.compress_type  = zipfile.ZIP_DEFLATED
     cbdata            = urllib2.urlopen('%s/%s' % (url, artifact)).read()
     zfile.writestr(cb, cbdata)

     # Generate the info.json file object.
     ij                = zipfile.ZipInfo()
     ij.filename       = 'info.json'
     ij.date_time      = time.localtime()[:6]
     ij.compress_type  = zipfile.ZIP_DEFLATED
     ijdata            = json.dumps({
               'name': 'Craftbukkit',
        'description': 'Basic bukkit server binary',
             'author': 'Bukkit Team',
            'website': 'http://bukkit.org',
            'version': '0.0.1-b%s' % build,
         'bukkit_min': build,
         'bukkit_max': build,
             'branch': branch,
         'categories': ['SERVER',],
       'dependencies': {'required': [], 'optional': []},
           'pkg_type': 'server',
                'api': api
     })
     zfile.writestr(ij, ijdata)
     
     lib               = zipfile.ZipInfo()
     lib.filename      = 'lib/._'
     lib.date_time     = time.localtime()[:6]
     lib.compress_type = zipfile.ZIP_DEFLATED
     zfile.writestr(lib, '')
     
     etc               = zipfile.ZipInfo()
     etc.filename      = 'etc/._'
     etc.date_time     = time.localtime()[:6]
     etc.compress_type = zipfile.ZIP_DEFLATED
     zfile.writestr(etc, '')
     
     zfile.close()
     zf.close()

def log(level, msg):
  logfile = open(_config('Settings', 'logfile', 'path'), 'a')
  logfile.write('[%15s][%7s] %s\n' % (datetime.datetime.now().ctime(),
                                      level.upper(), msg))
  logfile.close()

def main():
  # First we need to initialize the database if it hasnt been already.  This
  # will create the database table if it doesn't exist.
  BukGetPkg.metadata.create_all(engine)
  UserAPI.metadata.create_all(engine)

  session       = get_session()
  if session.query(UserAPI).filter_by(username = 'Bukkit Team').first() is None:
    bukkit_api  = UserAPI('Bukkit Team', 'bukkit@bukkit.org')
    bukkit_api.activated = True
    print 'New Bukkit Team API Generated: %s' % bukkit_api.api
    session.add(bukkit_api)
    session.commit()
  session.close()
  
  # Next we need to generate the bukkit server packages and place them into
  # the uploads directory.
  generate_bukkit_packages()
  
  # Now we work through all of the packages that are in the uploads directory
  # and try to import them into the repository.
  session       = get_session()
  for item in os.listdir(_config('Settings', 'uploads', 'path')):
    package     = BukGetPkg(item)
    log('info', '[%s] %s version %s returned with status: %s.' %\
        (item, package.name, package.version, package.status))
    if package.valid:
      # Now we will try to add the package to the repository.  If the database
      # change sticks (i.e. there are no conflicts and the database is up), then
      # the row will be commited.
      package.prep()
      try:
        session.add(package)
        session.commit()
      except:
        log('info', '%s version %s %s' %\
            (package.name, package.version, 'Existing Package Error'))
        package.remove()
      else:
        package.move()
        log('info', '%s version %s %s' %\
            (package.name, package.version, package.status))
  session.close()
  
  # Now we need to generate the repo.json dictionary.  We will query the
  # database for all of the packages and then iterate through them, running
  # the json function within the object to generate the dictionary.
  session       = get_session()
  packages      = session.query(BukGetPkg)
  session.close()
  log('info', 'Generating New Repository Dictionary...')
  pkgs = {'packages': []}
  for package in packages:
    pkgs['packages'].append(package.dump())
    log('info', '%s version %s Added to the repository dictionary' %\
      (package.name, package.version))
  
  # Next we write the dictionary to file.
  repo = open(os.path.join(\
      _config('Settings', 'repository', 'path'), 'repo.json'), 'w')
  repo.write(json.dumps(pkgs))
  repo.close()
  
  # Lastly we need to clean up any orphaned packages.
  # NOTE: This will be implimented down the road.

if __name__ == '__main__':
  sys.exit(main())