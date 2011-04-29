#!/usr/bin/env python
import os
import sys
import cmd
import ConfigParser
import datetime
import json
import zipfile
import hashlib
from StringIO import StringIO
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy                 import Table, Column, Integer, String, \
                                       DateTime, Date, ForeignKey, Text, \
                                       Boolean, create_engine, MetaData, and_
from sqlalchemy.orm             import relation, backref, sessionmaker

Base      = declarative_base()
version   = 'POCb1'
slogans   = [
  'No witty remarks yet.',
]
motd      = '''
BukGet Repository Client Version %s
----------------------------------------
POC Alpha build.  No Information

bukget> %s
''' % (version, slogans[random(0,len(slogans)-1)])

class Package(Base):
  '''
  This is the base package class.  It has all the information that is specific
  to this version of this package.
  '''
  __tablename__ = 'packages'
  _env          = os.path.join(sys.path[0],'env')
  _repo         = os.path.join(sys.path[0],'repo')
  _cache        = os.path.join(_repo,'cache')
  _plugins      = os.path.join(_env,'plugins')
  name          = Column(String, primary_key=True)
  author        = Column(String, primary_key=True)
  version       = Column(String, primary_key=True)
  description   = Column(Text)
  branch        = Column(String)
  pkg_type      = Column(String)
  website       = Column(String)
  categories    = Column(Text)
  required_deps = Column(Text)
  optional_deps = Column(Text)
  bukkit_min    = Column(Integer)
  bukkit_max    = Column(Integer)
  url           = Column(String)
  checksum      = Column(String)
  installed     = Column(Boolean)
  
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
  
  def __init__(self, **args):
    self.name         = args['name']
    self.author       = args['author']
    self.description  = args['description']
    self.branch       = args['branch']
    self.pkg_type     = args['pkg_type']
    self.website      = args['website']
    self.version      = args['version']
    self.url          = args['location']
    self.checksum     = args['checksum']
    self.installed    = False
    self.bukkit_min   = args['bukkit_min']
    self.bukkit_max   = args['bukkit_max']
    self.set_deps(args['dependencies'])
    self.set_cats(args['categories'])
  
  def install(self):
    pkg_path    = os.path.join(self._cache, self.checksum)
    try:
      md5       = hashlib.md5()
      pkgstream = urllib2.urlopen(self.url).read()
      md5.update(pkgstream)
      if md5.hexdigest() == self.checksum:
        zipdata = StringIO()
        zipdata.write(pkgstream)
      else:
        pkgfile.close()
        raise 'CheckSumError'
      
      pkg       = zipfile.ZipFile(zipdata)
      pkg.extractall(pkg_path)
      
          
      
  
  def remove(self):
    pass
  