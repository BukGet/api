import os
import sys
from commands import getoutput as run
import config
import logging

class Bukkit(object):
  '''
  This class handles any actions that revolve around the bukkit server itself.
  This includes starting, stopping, updating, etc.
  '''
  mem_min   = 512
  mem_max   = 1024
  version   = 0
  branch    = 'stable'
  _artifact = 'artifact/target/craftbukkit-0.0.1-SNAPSHOT.jar'
  _base     = 'http://ci.bukkit.org/job/dev-CraftBukkit'
  _branch   = {
   'stable': 'promotion/latest/Recommended',
     'test': 'lastStableBuild',
      'dev': 'lastSuccessfulBuild',
      
  }
  
  def __init__(self):
    # The only thing that we really need to do is make sure that we have a
    # valid configuration loaded.
    self.reload_config()
  
  def reload_config(self):
    '''
    Updates the object to match the configuration settings.
    '''
    try:
      self.mem_min  = config.get('Bukkit', 'memory_min', 'int')
      self.mem_max  = config.get('Bukkit', 'memory_max', 'int')
      self.version  = config.get('Bukkit', 'version')
      self.branch   = config.get('Bukkit', 'code_branch')
    except:
      self.update_config()
  
  def update_config(self):
    '''
    Inverse of reload_config.  Updates the config file to match the object.
    '''
    config.set('Bukkit', 'memory_min', self.mem_min)
    config.set('Bukkit', 'memory_max', self.mem_max)
    config.set('Bukkit', 'version', self.version)
    
  def download(self, branch='stable', build=None):
    if build is not None:
      # If we are downloading a specific build number, then we don't have to
      # bother parsing the ci page to pull the build number.
      build_no  = build
      url       = '%s/%s/%s' % (self._base, build, self._artifact)
    else:
      # In this case, the user just wants to pull the latest version in the
      # specified branch.  Because of this, we need to parse the ci page
      # associated with the branch in order to know what build of bukkit
      # we are infact pulling down.
      url = '%s/%s/%s' % (self._base, self._branch[branch], self._artifact)
      try:
        title     = re.compile("<title>.*#(\d+).*<\/title>",re.DOTALL|re.M)
        page      = urllib2.urlopen('%s/%s' %\
                                (self._base, self._branches[branch])).read()
        build_no  = int(title.findall(page)[0])
      except:
        logging.log('ERROR: Branch slug led to a page without version info.')
        return False
    try:
      # New we will start doing the actual work.  This block of code will
      # handle downloading and writing to disk the new bukkit build.
      cb_data   = urllib2.urlopen(url).read()
      cb_binary = open(os.path.join(config.get('Paths', 'env'), 
                        '.craftbukkit.jar'), 'wb')
      cb_binary.write(cb_data)
      cb_binary.close()
    except:
      logging.log('ERROR: Download of new bukkit build %s failed.' % build_no)
      return False
    if not self.running():
      shutil.move(os.path.join(config.get('Paths','env'), '.craftbukkit.jar'),
                  os.path.join(config.get('Paths','env'), 'craftbukkit.jar'))
      self.branch   = branch
      self.version  = build_no
      self.update_config()
      return True
    else:
      logging.log('ERROR: Cannot update bukkit while it is running!')
      return False
  
  def start(self):
    '''
    Starts the bukkit server.
    '''
    # NOTE: Currently this code is *nix/Cygwin specific as its using screen.
    #       This is planned to be depricated out in favor of an XMLRPC type
    #       interface to the bukkit server instead.  As this is currently not
    #       on the high-priority list to replace at the moment, it will be
    #       left in until a proper backgrounding technique can be used that
    #       does not require using 3rd party tools that lock this into a
    #       portability issue.
    
    # This looks faily complicated, however its simply trying to build a
    # command that will cd into the bukkit environment, then start a screen
    # session that automatically launches the bukkit server in such a way that
    # if the bukkit server stops or dies, the screen session will die as well.
    java      = run('which java')
    startup   = '%s -Xms%sm -Xmx%sm -jar craftbukkit.jar nogui' %\
                (java, self.mem_min, self.mem_max)
    screen    = 'screen -dmS bukkit_server bash -c \'%s\'' % startup
    command   = 'cd %s;%s' % (config.get('Paths', 'env'), screen)
    if not self.running():
      run(command)
  
  def stop(self):
    '''
    Stops the bukkit server.
    '''
    # NOTE: Currently this code is *nix/Cygwin specific as its using screen.
    #       This is planned to be depricated out in favor of an XMLRPC type
    #       interface to the bukkit server instead.  As this is currently not
    #       on the high-priority list to replace at the moment, it will be
    #       left in until a proper backgrounding technique can be used that
    #       does not require using 3rd party tools that lock this into a
    #       portability issue.
    if self.running():
      self.command('stop')
  
  def running(self):
    '''
    Functions simply returns if the bukkit server is running or not.
    '''
    # NOTE: Currently this code is *nix/Cygwin specific as its using screen.
    #       This is planned to be depricated out in favor of an XMLRPC type
    #       interface to the bukkit server instead.  As this is currently not
    #       on the high-priority list to replace at the moment, it will be
    #       left in until a proper backgrounding technique can be used that
    #       does not require using 3rd party tools that lock this into a
    #       portability issue.
    output = run('screen -wipe bukkit_server')
    if output[:20] == 'There is a screen on':
      return True
    else:
      return False
  
  def command(self, command):
    if self.running():
      run('screen -S bukkit_server -p0 -X stuff \'%s\n\'' % command)
  
  def time(self, time_of_day):
    '''
    Sets the time of day to a specific server-time.  This can either be
    invoked using the numeric time or by using the hard-coded strings:
      dawn, midday, dusk, midnight
    '''
    times = {
          'dawn': 00000,
        'midday': 06000,
          'dusk': 12000,
      'midnight': 18000,
    }
    if time_of_day in times:
      time_of_day = times[time_of_day]
    self.command('time set %s' % time_of_day)
  
  def message(self, message):
    '''
    Sends a message to all players on the server.
    '''
    if self.running():
      self.command('say %s' % message)
  
  def player_op(self, player):
    pass