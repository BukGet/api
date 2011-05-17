import cmd
import logging
import config
import bukkit
import pkg

class Commands(cmd.Cmd):
  intro   = motd
  prompt  = 'bukget>'
  
  def __init__(self):
    self._parse_repository()
  
  def do_bukkit(self, s):
    '''bukkit [command] [options]
    This command houses all the functions related to the bukkit server
    itself.  this includes starting, stopping, updating, '''
    cmd = s.split()
    if len(cmd) > 1:
      BukkitCommands().onecmd(s)
    else:
      BukkitCommands().cmdloop()
  
  def do_pkg(self, s):
    cmd = s.split()
    if len(cmd) > 1:
      PackageCommands().onecmd(s)
    else:
      PackageCommands().cmdloop()
  
  def do_player(self, s):
    cmd = s.split()
    if len(cmd) > 1:
      PlayerCommands().onecmd(s)
    else:
      PlayerCommands().cmdloop()
  
  def do_snapshot(self, s):
    pass
  
  def do_backup(self, s):
    pass
  
  def do_ip(self, s):
    pass
  
  def do_time(self, s):
    pass
  
  def do_msg(self, s):
    pass
  
  def do_update(self, s):
    pass

class BukkitCommands(cmd.Cmd):
  prompt  = 'bukget[BUKKIT]>'
  bukkit  = bukkit.Bukkit()
  
  def do_info(self, s):
    '''info
    Returns the version information, branch information, and running status
    of the bukkit server.
    '''
    status  = {True: 'running', False: 'stopped'}
    print 'Current Bukkit Build %s on Branch %s is currently %s.' %\
          (self.server.version, 
           self.server.branch, 
           status[self.server.running()])
  
  def do_start(self, s):
    '''start
    Starts the bukkit server.
    '''
    if not self.server.running():
      self.server.start()
      print 'Server has started.'
    else:
      print 'Server already running!'
  
  def do_stop(self, s):
    '''stop
    Stops the bukkit server.
    '''
    if self.server.running():
      self.server.stop()
      print 'Server shutdown initiated.'
    else:
      print 'Server already stopped!'
  
  def do_console(self, s):
    '''console
    Presents the user the server console.  When the user wants to exit the
    console they must use the following key combinations: Cntrl+a then d.
    '''
    if self.server.running():
      os.system('screen -DRS bukkit_server')
    else:
      print 'Could not connect to console.'
  
  def do_upgrade(self, s):
    '''upgrade [branch/build number]
    Upgrades the installed bukkit version to the requested branch or build
    number.
    '''
    if not self.server.running():
      self.server.download(s)
  
  def do_return(self, s):
    '''return
    Returns the user back to the main command prompt.  This is mostly used
    if the user is using interactive mode.
    '''
    pass

class PlayerCommands(cmd.Cmd):
  prompt  = 'bukget[PLAYER]>'
  server  = bukkit.Bukkit()
  
  