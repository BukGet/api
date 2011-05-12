from ConfigParser import ConfigParser
import os, sys

def get(stanza, option):
  '''
  Open the configuration file and pull the value fromt he stanza and option
  specified.  Optionally the option type can be overriden with opt_type to
  return any of the following types: string, bool, float, and int.
  '''
  config = ConfigParser.ConfigParser()
  config.read(os.path.join(sys.path[0],'config.ini'))
  if opt_type == 'string':
    return config.get(stanza, option)
  if opt_type == 'int':
    return config.getint(stanza, option)
  if opt_type == 'bool':
    return config.getboolean(stanza, option)
  if opt_type == 'float':
    return config.getfloat(stanza, option)
  if opt_type == 'path':
    return os.path.normpath(config.get(stanza, option))

def set(stanza, option, value):
  '''
  Opens the configuration file and sets the option specified to the value
  given within the stanza.  If the stanza does not exist, it will create it.
  '''
  config = ConfigParser.ConfigParser()
  config.read(os.path.join(sys.path[0],'config.ini'))
  if not config.has_section(stanza):
    config.add_section(stanza)
  config.set(stanza, option, value)
  config.write()