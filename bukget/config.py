from ConfigParser import ConfigParser
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

class Configuration(object):
    '''
    Configuration Object:
    
    This object houses all of the configuration data for the 
    '''
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
        self.parents = [for x in c.get('Settings', 'parents').split(','),
                        x.strip()]
        self.port = c.getint('Settings', 'port')
        self.host = c.get('Settings', 'host')
        self.debug = c.getboolean('Settings', 'debug')
        self.delay = c.getint('Settings', 'delay')
        self.server = c.get('Settings', 'server')
        self.virtualenv = c.getboolean('Settings', 'virtual_env')
        self.speedy = c.getboolean('Settings', 'speed_load')
        self.db_string = c.get('Settings', 'db_string')
        

class Database(object):
    '''
    Database Connection Object:
    
    This object simply connects to the database and sets up a session factory
    '''
    engine = None
    maker = None
    
    def __init__(self):
        conf = Configuration()
        self.engine = create_engine(conf.db_string)
        self.maker = sessionmaker(bind=self.engine)
        