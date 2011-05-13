import json
import urllib2
import hashlib
import re
import logging
import config
import pkg
from xenforo                    import XenForo
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy                 import Table, Column, Integer, String, \
                                       DateTime, Date, ForeignKey, Text, \
                                       Boolean, create_engine, MetaData, and_
from sqlalchemy.orm             import relation, backref, sessionmaker

Base          = declarative_base()

class PackageRepository(Base):
  '''
  This class handles all functions that involve talking to the repository
  database.  This includes updates, validation, activation, etc.
  '''
  __tablename__ = 'repositories'
  id            = Column(Integer(6), primary_key=True)
  maintainer    = Column(String(32))
  email         = Column(String(128))
  url           = Column(Text)
  plugin        = Column(String(32))
  hash          = Column(String(32))
  #last          = Column(String(32))
  activated     = Column(Boolean)
  created       = Column(DateTime)
  json          = None
  
  def _hashme(self, value):
    md5   = hashlib.md5()
    md5.update(value)
    return md5.hexdigest()
  
  def update(self):
    if self.activated:
      try:
        # First thing we need to get the json dictionary.  If for some reason
        # fetching the data results in an error, we need to catch the
        # exception thrown and log the output.
        data        = urllib2.urlopen(self.url).read()
      except:
        logging.log('ERROR: Could not read %s\'s plugin url.' % self.plugin)
        return False
      
      try:
        # Next we will run the dictionary through the jdon parser so that we
        # can get back a native dictionary.  If any errors are thrown we need
        # to make sure to catch them and log the error.
        dictionary  = json.loads(data)
      except:
        logging.log('ERROR: Json format for %s is invalid.' % self.plugin)
        return False
      
      # Next we will use the package module's logic to determine if the json
      # if valid.  This is a simple matter of making sure that the parent
      # object and all child objects have a valid flag set to True.
      package       = pkg.Package(dictionary)
      if package.valid:
        for version in package.versions:
          if not version.valid:
            logging.log('ERROR: Dictionary format for %s '+\
                        'isn\'t what is expected' % self.plugin)
            return False
      else:
        logging.log('ERROR: Dictionary format for %s '+\
                    'isn\'t what is expected' % self.plugin)
        return False
      
      # Everything looks good.  Lets set the objects json dictionary and
      # return a positive result ;)
      self.json     = dictionary
      return True
    else:
      logging.log('INFO: %s is not activated.' % self.plugin)
  
  def generate_activation_code(self):
    try:
      # First we need to get the plugin listings from plugins.bukkit.org.
      # We use this data to check to make sure that the plugin has been
      # "approved" by the bukkit team.  Unfortunately there isn't a better
      # way to handle this without completely breaking away from bukkit's
      # own submission process.  If there is an error, as always we need to
      # trap it and log the error.
      plugins   = json.loads(\
                    urllib2.urlopen(\
                      'http://plugins.bukkit.org/data.php').read())
    except:
      logging.log('ERROR: Could not pull a valid forum listing from bukkit.')
      return False
    try:
      # Next we will pull the package.json file and parse it directly into
      # sa package object.  As there is enough logic in the Package class
      # to be able to handle any errors that are thrown here, this should not
      # pose any kind of an issue.  We will be using primarially the authors
      # list in the package to make sure that the person tagged as the
      # maintainer as well as the person that owns the forum thread are listed
      # in in the authors list.  This approach is a compromise reached with
      # the devs in #bukkitdev as most of the plugins seen have multiple
      # developers and the stricter check was causing the need for a lot of
      # manual activation.
      plugin    = pkg.Package(json.loads(urllib2.urlopen(self.url)))
    except:
      logging.log('ERROR: Could not pull a valid '+\
                  'package.json from %s for activation' % self.plugin)
      return False
    name_rex    = re.compile(r'^(?:\[.+?\]){0,1}\s{0,1}(\w+[^ ])')
    
    # New we will need to iterate through the plugin list from bukkit and
    # search for the forum thread that we want.  Once we find it we want to
    # make sure that the package maintainer as well as the thread owner are
    # listed in the authors list.
    for item in plugins:
      name      = name_rex.findall(item['title'])
      if len(name) > 0:
        if name[0].lower() == self.plugin.lower() and\
           item['author'] in plugin.authors and\
           self.maintainer in plugin.authors:
          # Now we need to communicate with the forum so that we can send
          # a private message to the package maintainer to make sure that
          # they acknowledge that they are whom they say they are.
          forum = XenForo(config.get('Forums', 'username'),
                          config.get('Forums', 'password'),
                          config.get('Forums', 'hostname'))
          if fourm.login():
            date      = datetime.datetime.now().ctime()
            self.hash = self._hashme('%s%s%s' %\
                                    (self.plugin, self.maintainer, date))
            forum.private_message(self.maintainer,
                                  'BukGet Activation Code',
                                  self._gen_act_msg())
            logging.log('INFO: Activation PM for %s sent.' % self.plugin)
            return True
    logging.log('ERROR: Activation PM for %s was not sent.' % self.plugin)
    return False
  
  def _gen_act_msg(self):
    '''
    Generates the activation private message that is used as part of the
    activation sequence.
    '''
    return '''
      <p>Dear Plugin Developer</p>
      <p>Your account has recently been tagged with a new plugin repository 
      on our server.  In order to validate that you really did request a new 
      repository entry for %s, we are asking you to click the link below to 
      validate yourself so that we may activate this entry in our records.</p>
      <p>
        <a href="http://bukget.org/activate.php?hash=%s">ACTIVATION LINK</a>
      </p>
    ''' % (self.plugin, self.hash)
