from sqlalchemy import (Table, Column, Integer, String, DateTime, Date, 
                        ForeignKey, Text, Boolean, MetaData, 
                        and_, desc)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, joinedload, subqueryload
import datetime
import time
import yaml

Base = declarative_base()

def init(engine):
    '''
    Initializes the Databases
    '''
    Plugin.metadata.create_all(engine)
    Version.metadata.create_all(engine)
    Meta.metadata.create_all(engine)
    History.metadata.create_all(engine)

def _list_parser(s):
    '''
    Internal Method:
    
    Parses the incoming strint and returns a list.
    '''
    if isinstance(slist, unicode) or isinstance(slist, str):
        data = slist.split(',')
    else:
        data = slist
    vals = []
    for item in data:
        vals.append(item.strip())
    return vals

class Plugin(Base):
    '''
    Plugin Object:
    
    This is the database object for a plugin.
    '''
    __tablename__ = 'plugin'
    name = Column(String(128), unique=True)
    plugin_name = Column(String(128))
    categories = Column(Text)
    authors = Column(Text)
    status = Column(String(32))
    link = Column(Text)
    versions = relationship('Version', order_by='desc(Version.date)', 
                            backref='plugin')
    
    def __init__(self, name, authors, categories, link, status, text):
        '''
        Initializes a new Plugin.
        
        Required:
            name        Plugin Slug Name (Must be unique)
            authors     List of plugin authors
            categories  List of plugin categories
            link        Link to the plugin on DBO
            status      DBO status for the plugin
            fname        Full name (The displayed text) of the plugin on DBO
        '''
        self.name = name
        self.link = link
        self.update(authors=authors, categories=categories, status=status,
                    fname=fname)

    def update(self, authors=None, categories=None, status=None, fname=None):
        '''
        Update plugin information
        
        Optionally updates the information related to the plugin.
            authors         List of plugin authors
            categories      List of plugin categories
            status          Status string
            text            Full name (The displayed text) of the plugin on DBO
        '''
        if authors is not None:
            self.authors = ', '.join(_list_parser(authors))
        if categories is not None:
            self.categories = ', '.join(_list_parser(categories))
        if status is not None:
            self.status = status
        if fname is not None:
            try:
                json.dumps(fname)
                self.plugin_name = fname
            except:
                self.plugin_name = None

    def get(self, item):
        '''
        Gets list item.
        
        Returns a properly formatted list of either the authors or categories
        database items.
        
        Required:
            item        Either 'authors' or 'categories'
        '''
        if item == 'authors':
            return _list_parser(self.authors)
        if item == 'categories':
            return _list_parser(self.categories)
        return None
    
    def dict(self):
        '''
        Returns the python dictionary representation of the object.
        '''
        data = {
            'name': self.name,
            'plugin_name': self.plugin_name,
            'bukkitdev_link': self.link,
            'status': self.status,
            'authors': self.get('authors'),
            'categories': self.get('categories'),
            'versions': []
        }
        for ver in self.versions:
            data['versions'].append(ver.dict())
        return data


class Version(Base):
    '''
    Version Object:
    
    '''
    __tablename__ = 'version'
    id = Column(Integer(8), primary_key=True)
    name = Column(String(32))
    link = Column(Text)
    date = Column(DateTime)
    cb_versions = Column(Text)
    filename = Column(String(32))
    md5 = Column(String(32))
    hard_dependencies = Column(Text)
    soft_dependencies = Column(Text)
    plugin_id = Column(Integer(8), ForeignKey('plugin.id'))
    
    def __init__(self, name, link, cb_versions, filename, md5, 
                 soft_deps, hard_deps, plugin_id):
        '''
        Initialization of the Version object:
        
        Required:
            name            Name of the Version
            link            Link to the version file
            cb_versions     Bukkit RBs that this plugin is known to work with
            filename        Name of the plugin file
            md5             MD5 Sum of the version
            soft_deps       Soft dependencies needed for the plugin
            hard_deps       Hard (required) dependencies needed for the plugin
            plugin_id       Id of the plugin this version is associated with
        '''
        self.name = name
        self.link = link
        self.date = datetime.datetime.now()
        self.cb_versions = ', '.join(_list_parser(cb_versions))
        self.filename = filename
        self.md5 = md5
        self.hard_dependencies = ', '.join(_list_parser(hard_deps))
        self.soft_dependencies = ', '.join(_list_parser(soft_deps))
        self.plugin_id = plugin_id
    
    def get(self, item):
        '''
        Gets list item
        
        Returns a properly formatted list of either the authors or categories
        database items.
        
        Required:
            item        Either cb_versions, soft_dependencies, 
                        or hard_dependencies
        '''
        if item == 'cb_versions':
            return _list_parser(self.cb_versions)
        if item == 'soft_dependencies':
            return _list_parser(self.soft_dependencies)
        if item == 'hard_dependencies':
            return _list_parser(self.hard_dependencies)
    
    def dict(self):
        '''
        Returns the python dictionary representation of the object.
        '''
        return {
            'name': self.name,
            'dl_link': self.link,
            'date': int(time.mktime(self.date.timetuple())),
            'filename': self.filename,
            'md5': self.md5,
            'game_builds': self.get('cb_versions'),
            'soft_dependencies': self.get('soft_dependencies'),
            'hard_dependencies': self.get('hard_dependencies'),
        }


class Meta(Base):
    '''
    Metadata Object
    '''
    __tablename__ = 'metadata'
    id = Column(Integer(8), primary_key=True)
    date = Column(DateTime)
    time = Column(Integer(8))
    history = relationship('History', backref='meta')
    
    def __init__(self):
        '''
        Initializes the Meta object.
        '''
        self.date = datetime.datetime.now()
    
    def finish(self):
        '''
        Finish is run when a DBO generation is complete.  this will set the
        duration times in the database.
        '''
        curtime = datetime.datetime.now()
        self.time = (curtime - self.start_time).seconds
    
    def dict(self):
        '''
        Returns the python dictionary representation of the object.
        '''
        data = {
            'id': self.id,
            'date': int(time.mktime(self.date.timetuple())),
            'duration': self.time,
            'changes': []
        }
        for ver in history:
            data['changes'].append(ver.dict())
        return data
    

class History(Base):
    __tablename__ = 'history'
    id = Column(Integer(8), primary_key=True)
    meta_id = Column(Integer(8), ForeignKey('metadata.id'))
    plugin_name = Column(Text)
    version_name = Column(Text)
    
    def __init__(self, meta_id, plugin, version):
        '''
        History initialization
        
        Required:
            meta_id     Meta object Id
            plugin      Plugin Name
            version     Version Name
        '''
        self.meta_id = meta_id
        self.plugin_name = plugin
        self.version_name = version
    
    def dict(self):
        '''
        Returns the python dictionary representation of the object.
        '''
        return {
            'plugin': self.plugin_name,
            'version': self.version_name
        }