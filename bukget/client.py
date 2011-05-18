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
    itself.  This includes starting, stopping, updating, etc.  For help on
    the available commands, type "bukkit help" and "bukkit help [command]"
    '''
    cmd = s.split()
    if len(cmd) > 1:
      BukkitCommands().onecmd(s)
    else:
      BukkitCommands().cmdloop()
  
  def do_pkg(self, s):
    '''pkg [command] [options]
    This command houses all the functions related to plugin and library
    packages.  This includes installing, upgrading, removing, etc.  For help
    on the available commands, type "pkg help" and "pkg help [command]"
    '''
    cmd = s.split()
    if len(cmd) > 1:
      PackageCommands().onecmd(s)
    else:
      PackageCommands().cmdloop()
  
  def do_player(self, s):
    '''player [command] [options]
    This command houses all the functions related to player control.  This
    includes banning, giving, opping, etc.  For help on the available
    commands, type "player help" and "player help command"
    '''
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
  
  def do_list(self, s):
    '''list
    Returns the list of players online.
    '''
    print 'Players online: %s' % ', '.join(self.server.player_list())
  
  def do_msg(self, s):
    '''msg [player] [message]
    Sends the message to the specified player.
    '''
    dset      = s.split()
    if len(dset) > 1:
      msg     = ' '.join(dset[1:])
      player  = dset[0]
      self.server.player_msg(player, msg)
      print 'Message sent to %s' % player
    else:
      print 'Not enough arguments.'
  
  def do_give(self, s):
    '''give [player] [item-id] [amount]
    Will give the player specified the amount (default 64) of the item
    requested.  The command will first parse the item definitions to see if
    the item-id is a known item within the system.  If not then it will fall
    back on simply sending the item-id given directly to the server.  For
    example:
    
      player give ManiacM4c stone
    
    is the same as:
    
      player give ManiacM4c 1
    '''
    dset = s.split()
    if len(dset) <= 2:
      print 'Not enough arguments.'
      return
    
    # Loading the item definition dictionary and parsing out the options
    idefs   = json.loads(open(os.path.join(config.get('Paths', 'config'),
                        'item_definitions.json'), 'r'))
    player  = dset[0]
    item_id = dset[1]
    
    # If the item id exists within the idem definition, then we need to get
    # the real item id and set that instead.
    if item_id in idefs:
      item_id = idefs[item_id]
    
    # if there is amount specified use that, otherwise wet it to 64.
    if len(dset) <= 3:
      amount = dset[3]
    else:
      amount = 64
    
    # Now to send the command to the server.
    self.server.player_give(player, item_id, amount)
    print 'Server instructed to give %s %s to %s' % (amount, item_id, player)
  
  
  