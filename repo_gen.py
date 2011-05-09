#!/usr/bin/env python
# encoding: utf-8
"""
repo_gen.py

Created by Steven McGrath on 2011-04-29.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import getopt
import urllib2
import json
import re
from BeautifulSoup              import BeautifulSoup    as bsoup
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy                 import Table, Column, Integer, String, \
                                       DateTime, Date, ForeignKey, Text, \
                                       Boolean, create_engine, MetaData, and_
from sqlalchemy.orm             import relation, backref, sessionmaker


sql_string    = ''
engine        = create_engine(sql_string)
Session       = sessionmaker(bind=engine)
Base          = declarative_base()

class RepoLink(Base):
  '''
  This class is what provides the links needed to retreive and build the
  repository.
  '''
  __tablename__ = 'repositories'
  data          = None
  status        = None
  id            = Column(Integer(6), primary_key=True)
  author        = Column(String(32))
  email         = Column(String(128))
  url           = Column(Text)
  plugin        = Column(String(32))
  activated     = Column(Boolean)
  validated     = Column(Boolean)
  ip_address    = Column(String(15))
  created       = Column(DateTime)
  
  def __init__(self, username, url):
    self.username = username
    self.url      = url
  
  def activate(self):
    #plu_dict      = json.loads(\
    #                  urllib2.urlopen(\
    #                    'http://plugins.bukkit.org/data.php').read())
    #name          = re.compile(r'^(?:\[.+?\]){0,1}\s(\w+[^ ])')
    #for item in plu_dict:
    #  plugin      = name.findall(item['title'])[0]
    #  if plugin.lower() == self.plugin.lower():
    #    if item['author'].lower() == self.author.lower():
    #      self.activated  = True
    #      return True
    return False
    
  
  def fetch(self):
    if self.activated:
      try:
        jdata           = urllib2.urlopen(self.url).read()
      except:
        self.status     = 'Could not Fetch Remote Repository Entries'
        return False
      
      try:
        data            = json.loads(jdata)
      except:
        self.status     = 'JSON Dictionary format invalid.'
        return False
      
      reqd_items        = ['name', 'author', 'website', 'categories', 
                           'dependencies', 'versions']
      for item in reqd_items:
        if item not in data:
          self.status   = 'Dictionary Base Items not Valid'
          return False
      
      reqd_ver          = ['version', 'branch', 'bukkit_min', 'bukkit_max',
                         'location', 'checksum']
      for item in reqd_ver:
        for entry in data['versions']:
          if item not in entry:
            self.status = 'Versioning Dictionary Items not Valid'
            return False
      
      if data['name'] != self.plugin:
        self.status     = 'Plugin Name Does Not Match'
        return False
      if data['author'] != self.author:
        self.status     = 'Plugin Author Does Not Match'
        return False
      
      self.data         = data
      return True
    else:
      self.status       = 'Not Activated'
      return False

def generate_repository():
  # if need to validate, sleep 1 sec.
  session = Session()
  links   = session.query(RepoLink)
  repo    = []
  for link in links:
    if not link.activated:
      link.activate()
    if link.fetch():
      repo.append(link.data)
      print '%s added to canonical repository.' % link.plugin
    else:
      print '%s failed with status: %s' % (link.plugin, link.status)
  rfile   = open('repo.json', 'w')
  rfile.write(json.dumps(repo))
  rfile.close()

if __name__ == '__main__':
  sys.exit(generate_repository())
  
  