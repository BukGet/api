#!/usr/bin/env python2.6
import cmd
import os
import sys
import ConfigParser
import time
import re
import shutil
import json
import urllib2
import datetime
from   commands      import getoutput     as run

motd  = '''BukGet Client Version 0.0.1-git
use the 'help' command for documentation.
'''

class Package(object):
  pass

class BukkitServer(object):
  def __init__(self):
    self.reload_config()
  
  def _command(self, command):
    if self.running():
      run('screen -S bukkit_server -p0 -X stuff \'%s\n\'' % command)
  
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
    configfile        = os.path.join(sys.path[0], 'config', 'bukget.ini')
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
    configfile        = os.path.join(sys.path[0], 'config', 'bukget.ini')
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
    need_players  = True
    while need_players:
      where       = logfile.tell()
      line        = logfile.readline()
      if not line:
        time.sleep(0.1)
        logfile.seek(where)
      else:
        plist     = plistr.findall(line)
        if len(plist) > 0:
          need_players  = False
          players       = plist[0]
    logfile.close()
    return players
      
  
  def time(self, time_of_day):
    times = {
      'dawn': 00000,
    'midday': 06000,
      'dusk': 12000,
  'midnight': 18000,
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
  
  def save_all(self):
    self._command('save-all')
    # need to check to see when this is completed.  watch the logfile.
    # Save complete.
    name          = os.path.join(self.env, 'server.log')
    complete      = re.compile(r'Save complete\.$')
    logfile       = open(name, 'r')
    size          = os.stat(name)[6]
    logfile.seek(size)    
    done          = False
    while not done:
      where       = logfile.tell()
      line        = logfile.readline()
      if not line:
        time.sleep(0.1)
        logfile.seek(where)
      else:
        if len(complete.findall(line)) > 0:
          done    = True
    logfile.close()
  
  def save_off(self):
    self._command('save-off')
  
  def save_on(self):
    self._command('save-on')


class CLI(cmd.Cmd):
  intro   = motd
  prompt  = 'bukget> '
  server  = None
  _cdefs  = None
  _idefs  = None
  _repo   = None
  
  def __init__(self):
    cmd.Cmd.__init__(self)
    self._prepare()
    self._refresh()
    self.server = BukkitServer()
  
  def do_update(self, s):
    '''update

    Updates the repository, configuration definitions, and item definitions.
    '''
    base  = 'https://github.com/SteveMcGrath/bukget/raw/master/definitions/'
    urls  = {
        'item': {
         'url': '%s/item_definitions.json' % base,
        'file': os.path.join(sys.path[0], 'config', 'item_definitions.json')
      },
      'config': {
         'url': '%s/configuration_definitions.json' % base,
        'file': os.path.join(sys.path[0], 'config', 'config_definitions.json')
      },
        'repo': {
         'url': 'http://bukget.org/repo.json',
        'file': os.path.join(sys.path[0], 'config', 'repository.json')
      }
    }

    for item in urls:
      print '[*] Attempting to Update %s' % urls[item]['file']
      try:
        ufile = open(urls[item]['file'], 'w')
        ufile.write(urllib2.urlopen(urls[item]['url']).read())
        ufile.close()
      except:
        print '[!] Update Failed for %s' % urls[item]['file']
      else:
        print '[*] Update Successful for %s' % urls[item]['file']
  
  def _refresh(self):
    self._cdefs = json.load(open(os.path.join(sys.path[0], 'config', 
                                  'config_definitions.json'), 'r'))
    self._idefs = json.load(open(os.path.join(sys.path[0], 'config', 
                                  'item_definitions.json'), 'r'))
    self._repo  = json.load(open(os.path.join(sys.path[0], 'config',
                                  'repository.json'), 'r'))
  
  def _prepare(self):
    '''prepare
    
    Prepares a stock server to be able to run bukkit.  This includes
    installing any needed software (like java) that is needed to be able to
    run.
    '''
    
    # Sets up the directory tree
    if not os.path.exists(os.path.join(sys.path[0], 'env')):
       os.makedirs(os.path.join(sys.path[0], 'env'))
    if not os.path.exists(os.path.join(sys.path[0], 'env', 'plugins')):
      os.makedirs(os.path.join(sys.path[0], 'env', 'plugins'))
    if not os.path.exists(os.path.join(sys.path[0], 'backup')):
      os.makedirs(os.path.join(sys.path[0], 'backup', 'worlds'))
      os.makedirs(os.path.join(sys.path[0], 'backup', 'snapshots'))
    if not os.path.exists(os.path.join(sys.path[0], 'config')):
      os.makedirs(os.path.join(sys.path[0], 'config'))
      self.do_update(None)
    
    # Checks to see if screen and java is installed.
    need_deps   = False
    for package in ['java', 'screen']:
      output    = run('which %s' % package)
      rhel      = re.compile(r'which:\sno\s%s' % package)
      if len(rhel.findall(output)) > 0:
        need_deps = True
      if output == '':
        need_deps = True
    
    if need_deps:
      print '\nWARNING\n-------\n'
      print 'Before you continue, please perform the following operations\n'+\
            'to install the needed software to get bukget working.  We\n'+\
            'depend on this software in order to properly background and\n'+\
            'and run the bukkit server.  As it is expected for this\n'+\
            'script to be run as a non-privileged user, we should not\n'+\
            'be able to run these commands on our own.\n'
      
    if sys.platform == 'darwin':
      # Nothing should be needed here at the moment.  Apple provides screen
      # and a JVM that works.
      pass
    if sys.platform == 'linux2':
      if run('which apt-get') == '/usr/bin/apt-get':
        if need_deps:
          print 'sudo apt-get -y install openjdk-6-jre screen\n'
      elif run('which yum') == '/usr/bin/yum' :
        if need_deps:
          print 'yum -y install java-1.6.0-openjdk screen\n'
      else:
        if need_deps:
          print 'Please install java & screen.\n'
      # Configuration options that are specific to Linux
      pass
    else:
      pass
  
  def do_exit(self, s):
    '''Exits the CLI interface'''
    sys.exit()
  
  def do_pkg(self, s):
    '''pkg [command] [options]
    
    The pkg command handles all package management for things like plugins and
    libraries.  This includes installing, updating, and removing plugins.  As
    plugin developers have yet to conform to any standard for configuration
    types and naming conventions, you must manually configure any plugins.
    
    NOTE: CURRENTLY NON-FUNCTIONAL!
    
    Available Commands
    ------------------
      search [criteria]   Searches the package repository for any matching
                          information based on the criteria specified.
      list                Lists all installed packages.
      update              Updates the locally cached repository
      upgrade             Upgrades all packages to the ost current versions
                          that support the current bukkit build.
      install             Installs a package.
      remove              Removes a package.
    '''
    if len(s) > 1:
      options     = s.split()
      command     = options[0].lower()
      print 'None of the packaging commands are active yet!'
  
  def do_message(self, s):
    '''message [message]
    
    Sends a message to all players on the server.
    '''
    if self.server.running():
      self.server.message(s)
  
  def do_time(self, s):
    '''time [time-of-day]
    
    Sets the in-game time to the specified time.  You can either set the time
    based on numeric time (00000-24000) where 00000 represents dawn, or you
    can use one of the pre-determined times: dawn, midday, dusk, and midnight.
    '''
    if self.server.running():
      self.server.time(s)
  
  def do_ip(self, s):
    '''ip [command] [options]
    
    Performs any actions that pertain to a specific IP.  Currently the only
    available functions are banning and unbanning a IP from bring able to
    login to the server.
    
    Available Commands
    ------------------
      ip ban [ADDRESS]    Bans an IP Address from being able to login.
    
      ip pardon [ADDRESS] Removes a ban on an IP Address.
    '''
    if self.server.running():
      if len(s) > 1:
        options     = s.split()
        command     = options[0].lower()
        
        if command == 'ban' and len(options) >= 2:
          self.server.ip_ban(options[1])
        elif command == 'pardion' and len(options) >= 2:
          self.server.ip_pardon(options[1])
        else:
          print 'Invalid ip Command.'
      
  def do_player(self, s):
    '''player [command] [options]
    
    The player command handles any functions pertaining to players on the
    server.  This includes private messages, banning, kicking, 
    operator status, movement, and items.  Also getting the player list is
    handled here.
    
    Available Commands
    ------------------
      list         Lists all the online players. CURRENTLY BROKEN!
      
      message [PLAYER] [MESSAGE]
                          Sends the player a private message.
                          
      give [PLAYER] [ITEM] [AMOUNT]
                          Gives the specified player the item specified in the
                          amount specified.
                          
      teleport [PLAYER TO TELEPORT] [PLAYER TO TELEPORT TO]
                          Teleports the first player to the second player.
                          
      op [PLAYER]         Grants player operator (op) status.
      
      deop [PLAYER]       Removes operator status from a player.
      
      kick [PLAYER]       Kicks a player from the server.
      
      ban [PLAYER]        Bans a player from being able to login.
      
      pardon [PLAYER]     Removes a player ban.
    '''
    if self.server.running():
      if len(s) > 1:
        options     = s.split()
        command     = options[0].lower()
      
        if command == 'list':
          self.server.player_list()
        elif command == 'message' and len(options) >= 3:
          self.server.player_message(options[1], ' '.join(options[2:]))
        elif command == 'give' and len(options) >= 4:
          self.server.player_give(options[1], options[2], options[3])
        elif command == 'teleport' and len(options) >= 3:
          self.server.player_teleport(options[1], options[2])
        elif command == 'op' and len(options) >= 2:
          self.server.player_op(options[1])
        elif command == 'deop' and len(options) >= 2:
          self.server.player_deop(options[1])
        elif command == 'kick' and len(options) >= 2:
          self.server.player_kick(options[1])
        elif command == 'ban' and len(options) >= 2:
          self.server.player_ban(options[1])
        elif command == 'pardon' and len(optiions) >= 2:
          self.server.player_pardon(options[1])
        else:
          print 'Invalid player Command.'
  
  def do_snapshot(self, s):
    '''snapshot
    
    Snapshotting will take a complete backup of the server, including
    configurations, plugins, bukkit version, and world map.  The result will
    be a tarball of the entire environment.  Please not that this will require
    that the server be stopped before the operation can be performed.
    
    NOTE: Not Coded Yet.
    '''
    print 'Not Coded yet!'
  
  def do_backup(self, s):
    '''backup [worldname]
    
    This command will backup the world specified to a tarball. Backing up the 
    world will not require the server to stop, however disk i/o will be higher
    than normal during the backup and slowdowns can occur.
    '''
    if self.server.running():
      self.server.message('Starting Server-Wide World Save')
      self.server.save_all()
      self.server.save_off()
      self.server.message('Backing up World...')
      run('tar czvf backup/worlds/%s-%s.tar.gz %s/%s' % 
            (s,datetime.datetime.now().strftime('%y%m%d-%H%M%S'), 
             self.server.env, s))
      self.server.save_on()
      self.server.message('Backup Complete.')
      
  
  def do_bukkit(self, s):
    '''bukkit [command] [options]
    
    The Bukkit command handles anything pertaining to the server binary
    itself.  This includes starting, stopping, updating, and configuring the
    server.
    
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
      
      console             Connects to the screen console. In order to
                          disconnect fromt he console, you will need to press
                          CTRL+a then press d.
      
      config              Reconfigures the bukkit server. DOES NOT WORK YET
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
      elif command == 'message':
        if self.server.running():
          self.server.message()
      elif command == 'console':
        if self.server.running():
          os.system('screen -DRS bukkit_server')
      elif command == 'config':
        opt       = None
        value     = None
        if len(options) > 1:
          opt     = options[1].lower()
          if len(options) > 2:
            value = options[2].lower()
        
        # need to add configuration stuff here...
        pass
      else:
        print 'Invalid bukkit Command.'

if __name__ == '__main__':
  if len(sys.argv) > 1:
    CLI().onecmd(' '.join(sys.argv[1:]))
  else:
    CLI().cmdloop()