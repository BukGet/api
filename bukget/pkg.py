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
    plugins             = os.path.join(config.get('Paths', 'env'), 'plugins')
    os.remove(os.path.join(plugins, '%s.jar' % self.name))
    if purge:
      shutil.rmtree(os.path.join(plugins, self.name))
  
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
    # First we will try to download the package from the URL that we have on
    # hand.  If there is any issues then abort the install and log the event.
    # We will also go ahead and check the md5sum on file to make sure that
    # the file that we pulled is both the right file and not corrupt.
    try:
      package_file      = urllib2.urlopen(self.location).read()
      md5               = hashlib.md5()
      md5.update(package_file)
      if md5.hexdump() != self.checksum:
        logging.log('ERROR: Download of %s using %s was not valid.' %\
                    (self.name, self.location))
        return False
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
      # if the file is a zipfile, we will need to extract the file and then
      # parse out the data into the right locations.
      tmp_folder        = os.path.join(config.get('Paths','cache',self.name))
      zfile             = zipfile.ZipFile(tmp_filename)
      os.mkdir(tmp_folder)
      zfile.extractall(tmp_folder)
      zfile.close()
      
      # First thing we need to find the plugin jar file and move that into
      # the proper location. If the file exists and neither the upgrade or
      # force flags are set, then we need to error out and log the problem.
      for plugfile in os.listdir(os.path.join(tmp_folder, 'plugins')):
        if plugfile.lower() == '%s.jar' % self.name.lower():
          tmp_plug      = os.path.join(tmp_folder, 'plugins', plugfile)
          final_loc     = os.path.join(plugins, '%s.jar' % self.name)
          if not os.path.exists(final_loc) or\
                 force == True or\
                 upgrade == True:
            logging.log('INFO: Moving %s into place.' % plugfile)
            shutil.move(tmp_plug, final_loc)
          else:
            logging.log('ERROR: Installation of %s failed.'+\
                        'File %s already exists' % (self.name, final_loc))
            return False
      
      # Now we need to move on to the libraries that are bundled.  We will
      # simply iterate through all of the files in the folder and check to
      # see if they exist and move them as needed.
      for libfile in os.listdir(os.path.join(tmp_folder, 'lib')):
        tmp_lib       = os.path.join(tmp_folder, 'lib', libfile)
        final_loc     = os.path.join(plugins, libfile)
        if not os.path.exists(final_loc) or\
               force == True or\
               upgrade == True:
          logging.log('INFO: Moving %s into place.' % libfile)
          shutil.move(tmp_lib, final_loc)
      
      # Lastly we need to move any configuration files that are bundled to
      # their final resting place.  In order to do this we will first check
      # to see if the configuration directory even exists.  if it does then
      # we will run through the same checks to make sure we even want to
      # continue.  If so we will operate using the same method used for the
      # other two folders in the package.
      if not os.path.exists(os.path.join(plugins, self.name)) or\
             force == True or\
             upgrade == True:
        for configfile in os.listdir(os.path.join(tmp_folder, 'etc')):
          tmp_config    = os.path.join(tmp_folder, 'etc', configfile)
          final_loc     = os.path.join(plugins, self.name, configfile)
          if not os.path.exists(final_loc) or\
                 force == True or\
                 upgrade == True:
            logging.log('INFO: Moving %s into place.' % configfile)
            shutil.move(tmp_config, final_loc)
      
      # Now we need to clean up the mess we made for the package.  This is
      # fairly simple as we can just delete the zipfile and the extracted
      # directory.
      os.remove(tmp_filename)
      shutil.rmtree(tmp_folder)
      return True
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

def _gen_num_version(version):
  '''
  This function will take a version number and generate a numeric value based
  off of what it is able to pull.  Limitations require that the version format
  match any of the following:
  
  Without Varients
  ----------------
  X
  X.Y
  X.Y.Z
  
  With Varients
  -------------
  Xa
  X.Ya
  X.Y.Za
  
  Please note that it will only pull the first character of the varient. so in
  this case 0.0.1aa and 0.0.1.ab would equal the same number.
  '''
  vrex  = re.compile(r'(\d{1,3})')
  vmin  = re.compile(r'\d([a-z])')
  num   = 0
  pwr   = 1000000000
  for item in vrex.findall(version):
    num += int(int(item) * pwr)
    pwr = int(pwr / 1000)
  var   = vmin.findall(version.lower())
  if len(var) > 0:
    num += ord(var[0])
  return num

def is_ver_newer(orig, new):
  '''
  A simple function to compare the original version number to the new one and
  determine if the new one is really newer than the old one.  This will be
  useful to determine if an upgrade is needed.
  '''
  if _gen_num_version(orig) < _gen_num_version(new):
    return True
  else:
    return False

def is_ver_same(orig, new):
  '''
  A simple function to compare the original version number to the new one and
  determine if the new one is really the same than the old one.  This will be
  useful to determine if an upgrade is needed.
  '''
  if _gen_num_version(orig) == _gen_num_version(new):
    return True
  else:
    return False

def is_ver_older(orig, new):
  '''
  A simple function to compare the original version number to the new one and
  determine if the new one is really older than the old one.  This will be
  useful to determine if an upgrade is needed.
  '''
  if _gen_num_version(orig) > _gen_num_version(new):
    return True
  else:
    return False