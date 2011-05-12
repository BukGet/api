import os
import shutil
import urllib2
import zipfile
import datetime
import logging
import config

class Package(object):
  '''
  Base package class for BukGet  This class handles package validation,
  installation, upgrading, removal, and various checks that either the client
  or the server may need in order to perform their functions.
  '''
  name          = None
  description   = None
  author        = None
  website       = None
  categories    = []
  required_deps = []
  optional_deps = []
  versions      = []
  installed     = False
  installed_ver = None
  valid         = False
  
  def __init__(self, json_dict):
    # First thing we need to do is check to make sure the dictionary that has
    # been given to us is valid.  This should prevent any potential importing
    # issues down the road if we already know that the data in the file is
    # valid ;)
    if self._valid(json_dict):
      self.name           = json_dict['name']
      self.author         = json_dict['author']
      self.description    = json_dict['description']
      self.website        = json_dict['website']
      self.categories     = json_dict['categories']
      self.required_deps  = json_dict['required_dependencies']
      self.optional_deps  = json_dict['optional_dependencies']
      
      # Now we need to parse through all of the versions for this package.
      # In order to do this we will be relying on a child class that will
      # perform the heavy lifting.
      for version in json_dict['versions']:
        self.versions.append(PkgVersion(version, self.name))
      
      # As these 2 entries will only be present if the package is installed,
      # we cant force these.
      if 'installed': in json_dict:
        self.installed    = json_dict['installed']
        self.installed_ver= json_dict['installed_version']
  
  def _valid(self, json_dict):
    '''
    This function will check to see if the dictionary that we were given is
    valid and usable to import all the information we need.
    '''
    pass
  
  def _get_version(self, version_number):
    '''
    Will iterate through the versions list and return the requested PkgVersion
    object.
    '''
    for version in self.versions:
      if version.version == version_number:
        return version
      else:
        return None
  
  def install(self, version_number, force=False):
    '''
    Installs the specified version of the package into the bukkit environment.
    Optionally the force flag can be set, which will overwrite any existing
    files should they exist. 
    '''
    version   = self._get_version(version_number)
    if version is not None:
      version.install(force=force)
  
  def upgrade(self, version_number):
    '''
    Similar to install, however will only install the new java binary.  This
    function will not touch any existing configurations.
    '''
    version   = self._get_version(version_number)
    if version is not None:
      version.install(upgrade=True)
  
  def remove(self, purge=False):
    '''
    Removes any version of the package that is currently installed.  By
    default all configuration files are left behind incase the user woudl like
    to reference these files at a later date.  The optional purge flag will
    overwrite the behaviour and any configuration data will also be deleted. 
    '''
    pass
  
  def usable(self, bukkit_version):
    '''
    This function will simply check through the various versions of the
    package that is available and return if any versions of this package will
    work with the bukkit version that was specified.
    '''
    is_able     = False
    for version in self.versions:
      if version.usable(bukkit_version):
        is_able = True
    return is_able

class PkgVersion(object):
  '''
  This class pertains to a specific version of a package.  This class is what
  we will have actually doing most of the heavy-lifting and I/O operations.
  This class shouldn't be used without it's parent class however.
  '''
  name        = None
  version     = None
  location    = None
  checksum    = None
  branch      = None
  bukkit_min  = 0
  bukkit_max  = 0
  valid       = False
  
  def __init__(self, json_dict, name):
    # Just like in the parent class, we want to make sure the dictionary that
    # we were given is valid before doing anything.
    if self._valid(json_dict):
      self.version    = json_dict['version']
      self.location   = json_dict['location']
      self.checksum   = json_dict['checksum']
      self.branch     = json_dict['branch']
      self.bukkit_min = json_dict['bukkit_min']
      self.bukkit_max = json_dict['bukkit_max']
  
  def _valid(self, json_dict):
    '''
    This function will check to see if the dictionary that we were given is
    valid and usable to import all the information we need.
    '''
    pass
  
  def usable(self, bukkit_version):
    '''
    Determines if this package version is usable with a version of bukkit.
    '''
    if bukkit_version >= self.bukkit_min and\
       bukkit_version <= self.bukkit_max:
      return True
    else:
      return False
  
  def install(self, force=False, upgrade=False):
    '''
    Installs the package version into the bukkit environment.
    '''
    
    # First we will try to download the package fromt he URL that we have on
    # hand.  If there is any issues then abort the install and log the event.
    try:
      package_file      = urllib2.urlopen(self.location).read()
    except:
      logging.log('ERROR: Download of %s using %s failed.' %\
                  (self.name, self.location))
      return False
    # Set a name for the temporary package file.  We will be using this
    # throught the installation.
    tmp_filename        = os.path.join(config.get('Paths', 'cache'),
                                        '%s-%s' % self.name, self.version)
    plugins             = os.path.join(config.get('Paths', 'env'), 'plugins')
    
    # Now we actually need to write the file out to disk.  This is mainly
    # needed so that we can use some of the functionality of the zipfile
    # module to determine if the file is a zipfile.
    tmp_file            = open(tmp_filename, 'wb')
    tmp_file.write(package_file)
    tmp_file.close()
    
    # New we need to determine if the package is a zip file or a naked jar
    # file.
    if zipfile.is_zipfile(tmp_filename):
      pass
    else:
      # If the file is not a zip file, we will assume that the file we
      # downloaded was a jarfile and move it into the proper location.  I need
      # to figure out a way to check to make sure we really are moving a java
      # package and not some arbitrary file however.
      final_loc         = os.path.join(plugins, '%s.jar' % self.name)
      if not os.path.exists(final_loc) or force == True or upgrade == True:
        shutil.move(tmp_filename, final_loc)
        return True
      else:
        logging.log('ERROR: Installation of %s failed.'+\
                    'File %s already exists' % (self.name, final_loc))
        return False


