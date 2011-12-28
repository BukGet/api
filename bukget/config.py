from ConfigParser import ConfigParser

class Configuration(object):
    '''
    Configuration Object:
    
    This object houses all of the configuration data for the 
    '''
    is_parent = False
    parents = ['root.bukget.org',]
    port = 8082
    host = '127.0.0.1'
    debug = False
    delay = 2
    server = 'twisted'
    virtualenv = False
    speedy = True
    db_string = None
    
    def __init__(self):
        self.reload()
    
    def reload(self):
        '''
        Reloads the configuration file into the object.
        '''
        c = ConfigParser()
        c.read('bukget.ini')
        self.parents = [x.strip() for x in 
                        c.get('Settings', 'parents').split(',')]
        self.port = c.getint('Settings', 'port')
        self.host = c.get('Settings', 'host')
        self.debug = c.getboolean('Settings', 'debug')
        self.delay = c.getint('Settings', 'delay')
        self.server = c.get('Settings', 'server')
        self.virtualenv = c.getboolean('Settings', 'virtual_env')
        self.speedy = c.getboolean('Settings', 'speed_load')
        self.db_string = c.get('Settings', 'db_string')
        if c.has_option('Settings', 'is_parent'):
            self.is_parent = c.getboolean('Settings', 'is_parent')
        