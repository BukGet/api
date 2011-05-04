#!/usr/bin/env python
import cmd
import os
import sys
import ConfigParser
import re
import shutil
import urllib2
from   commands      import getoutput     as run

motd  = '''BukGet Client Version 0.0.1b1
'''

class Package(object):
  pass

class BukkitServer(object):
  def __init__(self):
    self.reload_config()
  
  def _command(self, command):
    if self.running():
      run('screen -S bukkit_server -p0 -X stuff \'%s\n\n\'' % command)
  
  def _set_defaults(self):
    '''
    Sets some sane default values needed for for the server to know
    what it is using.
    '''
    self.mem_min    = 512
    self.mem_max    = 1024
    self.version    = 0
    self.branch     = 'stable'
    self.env        = os.path.join(sys.path[0], 'env')
    self._artifact = 'artifact/target/craftbukkit-0.0.1-SNAPSHOT.jar'
    burl            = 'http://ci.bukkit.org/job/dev-CraftBukkit'
    self._branches = {
    'stable': '%s/promotion/latest/Recommended' % burl,
      'test': '%s/lastStableBuild' % burl,
       'dev': '%s/lastSuccessfulBuild' % burl,
    }
    self.update_config()
  
  def update_config(self):
    '''
    Updates the configuration file to match the object.
    '''
    config            = ConfigParser.ConfigParser()
    configfile        = os.path.join(sys.path[0], 'config.ini')
    # If the configuration file exists, then go ahead and load it into the
    # the config object.  Then go ahead to check to see if the Bukkit section
    # exists, and if it doesn't then add the section intot he loaded config.
    if os.path.exists(configfile):
      config.read(configfile)
    if not config.has_section('Bukkit'):
      config.add_section('Bukkit')
    # Now we will dump all of the relevent configuration settings into the
    # config object then for the object to save the settings to file.
    config.set('Bukkit', 'java_minimum_memory', self.mem_min)
    config.set('Bukkit', 'java_maximum_memory', self.mem_max)
    config.set('Bukkit', 'bukkit_version', self.version)
    config.set('Bukkit', 'code_branch', self.branch)
    config.set('Bukkit', 'artifact', self._artifact)
    config.set('Bukkit', 'environment_location', self.env)
    config.set('Bukkit', 'stable_branch_slug', self._branches['stable'])
    config.set('Bukkit', 'test_branch_slug', self._branches['test'])
    config.set('Bukkit', 'dev_branch_slug', self._branches['dev'])
    with open(configfile, 'wb') as confdump:
      config.write(confdump)
  
  def reload_config(self):
    '''
    Updates the object to match the configuration file.
    '''
    config            = ConfigParser.ConfigParser()
    configfile        = os.path.join(sys.path[0], 'config.ini')
    # If the configuration file exists and the Bukkit section exists within
    # the configuration file, then go ahead and import all of ths settings.
    # If either of these conditions do not match, then we will need to set
    # sane configuration defaults and then force the config update to make
    # the new settings stick.
    if os.path.exists(configfile):
      config.read(configfile)
      if config.has_section('Bukkit'):
        self.mem_min    = config.getint('Bukkit', 'java_minimum_memory')
        self.mem_max    = config.getint('Bukkit', 'java_maximum_memory')
        self.version    = config.getint('Bukkit', 'bukkit_version')
        self.env        = config.get('Bukkit', 'environment_location')
        self.branch     = config.get('Bukkit', 'code_branch')
        self._artifact = config.get('Bukkit', 'artifact')
        self._branches = {
          'stable': config.get('Bukkit', 'stable_branch_slug'),
            'test': config.get('Bukkit', 'test_branch_slug'),
             'dev': config.get('Bukkit', 'dev_branch_slug')
        }
      else:
        self._set_defaults()
    else:
      self._set_defaults()
      
  def upgrade_binary(self, branch=None):
    if not self.running():
      if branch is None:
        branch        = self.branch
      # Before we actually pull down the binary, we need to know what the
      # version number is that we are pulling down.  The 
      try:
        title         = re.compile("<title>.*#(\d+).*<\/title>",re.DOTALL|re.M)
        page          = urllib2.urlopen(self._branches[branch]).read()
        build_no      = int(title.findall(page)[0])
      except:
        return '[!] HTMLError: branch slug does not contain version number'
      if build_no > self.version:
        try:
          url           = '%s/%s' % (self._branches[branch], self._artifact)
          cb_data       = urllib2.urlopen(url).read()
          cb_binary     = open(os.path.join(self.env, '.craftbukkit.jar'), 'wb')
          cb_binary.write(cb_data)
          cb_binary.close()
        except:
          return '[!] IOError: could not successfully save binary'
        shutil.move(os.path.join(self.env, '.craftbukkit.jar'),
                    os.path.join(self.env, 'craftbukkit.jar'))
        self.branch   = branch
        self.version  = build_no
        self.update_config()
        return '[*] Success: Binary Updated'
      else:
        return '[*] Existing build is current'
  
  def start(self):
    if not self.running():
      java              = run('which java')
      startup           = '%s -Xms%sm -Xmx%sm -jar craftbukkit.jar' %\
                            (java, self.mem_min, self.mem_max)
      screen            = 'screen -dmLS bukkit_server bash -c \'%s\'' % startup
      command           = 'cd %s;%s' % (self.env, screen)
      run(command)
  
  def stop(self):
    if self.running():
      self._command('stop')
  
  def running(self):
    output = run('screen -wipe bukkit_server')
    if output[:20] == 'There is a screen on':
      return True
    else:
      return False
  
  def players(self):
    # look for Connected players:
    players       = []
    plistr        = re.compile(r'Connected players: .*')
    logfile       = open(os.path.join(self.env, 'server.log'), 'r')
    size          = os.stat(name)[6]
    logfile.seek(size)    
    need_players  = False
    while need_players:
      where       = logfile.tell()
      line        = logfile.readline()
      if not line:
        time.sleep(0.1)
        logfile.seek(where)
      else:
        plist     = plistr.findall(line)
        if len(plist) > 0:
          need_players  = True
          players       = plist[0]
    logfile.close()
    return players
      
  
  def time(self, time_of_day):
    times = {
      'dawn': 00000,
    'midday': 00000,
      'dusk': 00000,
  'midnight': 00000,
    }
    if time_of_day in times:
      time_of_day = times[time_of_day]
    self._command('time set %s' % time_of_day)
  
  def message(self, message):
    self._command('say %s' % message)
  
  def player_op(self, player):
    self._command('op %s' % player)
  
  def player_deop(self, player):
    self._command('deop %s' % player)
  
  def player_pm(self, player, message):
    self._command('tell %s %s' % (player, message))
  
  def player_give(self, player, item_id, item_num=64):
    self._command('give %s %s %s' % (player, item_id, item_num))
  
  def player_teleport(self, player, dest_player):
    self._command('tp %s %s' % (player, dest_player))
  
  def player_kick(self, player):
    self._command('kick %s' % player)
  
  def player_ban(self, player):
    self._command('ban %s' % player)
  
  def player_pardon(self, player):
    self._command('pardon %s' % player)
  
  def ip_ban(self, address):
    self._command('ban-ip %s' % address)
  
  def ip_pardon(self, address):
    self._command('pardon-ip %s' % address)


class CLI(cmd.Cmd):
  intro   = motd
  prompt  = 'bukget> '
  server  = BukkitServer()
  
  def do_prepare(self, s):
    '''prepare
    
    Prepares a stock server to be able to run bukkit.  This includes
    installing any needed software (like java) that is needed to be able to
    run.
    '''
    
    # Sets up the directory tree
    if not os.path.exists(self.server.env):
      os.makedirs(self.server.env)
    if not os.path.exists(os.path.join(self.server.env, 'plugins')):
      os.makedirs(os.path.join(self.server.env, 'plugins'))
    
    if sys.platform == 'darwin':
      # Configuration options that are specific to OSX
      pass
    if sys.platform == 'linux2':
      if run('which apt-get') is not None:
        pass
      elif run('which yum') is not None:
        pass
      else:
       pass
      # Configuration options that are specific to Linux
      pass
    else:
      pass
      
  def do_quit(self, s):
    '''Exits the CLI interface'''
    sys.exit()
    
  def do_bukkit(self, s):
    '''bukkit [command] [options]
    
    Available Commands
    ------------------
      info                Returns all available information on the current
                          bukkit server build.  This includes version, branch,
                          and running status.
      
      path                Sets the path for the server environment.  The
                          default is ./env.
                          
      upgrade [branch]    Upgrades the bukkit Binary to the current build. By
                          default upgrading will update within the same branch
                          the current build is in.
                          
      start               Starts the bukkit server instance.
      
      stop                Stops the bukkit server instance.
      
      configure           Reconfigures the bukkit server.
                          Note: DOES NOT WORK YET
    '''
    if len(s) > 1:
      options     = s.split()
      command     = options[0].lower()
    
      if   command == 'info':
        if self.server.running():
          status  = 'running'
        else:
          status  = 'stopped'
        print 'Current Bukkit Build %s on Branch %s is %s.' %\
          (self.server.version, self.server.branch, status)
      elif command == 'start':
        if not self.server.running():
          self.server.start()
        else:
          print '[!] Server Already Running!'
      elif command == 'stop':
        if self.server.running():
          self.server.stop()
        else:
          print '[!] Server Already Stopped!'
      elif command == 'upgrade':
        if not self.server.running():
          branch    = None
          if len(options) > 1:
            branch  = options[1]
          print self.server.upgrade_binary(branch)

if __name__ == '__main__':
  if len(sys.argv) > 1:
    CLI().onecmd(' '.join(sys.argv[1:]))
  else:
    CLI().cmdloop()