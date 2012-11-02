import json
import time
import datetime
import sqlalchemy.orm.collections as collections
from bukget.config import config
from sqlalchemy.ext.hybrid import Comparator, hybrid_property
from sqlalchemy import (Table, Column, Integer, ForeignKey, PickleType, Text,
                        Boolean, String, DateTime, and_, desc, create_engine)
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


class NewBase(object):
    # This is a base class that we will be using for the Database.
    # I am expanding upon the original declarative_base class and
    # adding in the json function (and potentially others) here in
    # order to conform to DRY principles ;)
    def json(self, *fields):
        '''json *fields
        Returns a Python Dictionary element with the items specified
        in the fields list.  If no items are specified, then return
        the endire dictionary.
        '''
        jdict = {}
        for attribute, value in vars(self).items():
            if (len(fields) == 0 or attribute in fields) and attribute[0] != '_':
                if isinstance(value, collections.InstrumentedList):
                    jdict[attribute] = [a.json() for a in value]
                elif isinstance(value, datetime.datetime):
                    jdict[attribute] = int(time.mktime(value.timetuple()))
                else:
                    if value is not None:
                        jdict[attribute] = value
                    else:
                        jdict[attribute] = ''
        return jdict



Base = declarative_base(cls=NewBase)

# This is the on-disk database
disk = create_engine(config.get('Settings', 'db_string'))
Session = sessionmaker(disk)


# The Category Association Table.  This table houses the relationships
# between plugins and categories.
catassc = Table('catagory_associations', Base.metadata,
    Column('plugin_id', Integer, ForeignKey('plugin.id')),
    Column('category_id', Integer, ForeignKey('category.id'))
)


# The Author Association Table.  This table houses the relationships
# between authors and plugins.
authassc = Table('author_association', Base.metadata,
    Column('author_id', Integer, ForeignKey('author.id')),
    Column('plugin_id', Integer, ForeignKey('plugin.id'))
)


def init(engine):
    Plugin.metadata.create_all(engine)
    Version.metadata.create_all(engine)
    Category.metadata.create_all(engine)
    Meta.metadata.create_all(engine)
    Author.metadata.create_all(engine)
    catassc.metadata.create_all(engine)
    authassc.metadata.create_all(engine)


class TextPickle(PickleType):
    # This is a simple overloaded pickler type so that we can embed JSON
    # into the database if needed.  This is mostly used with the Version
    # table, however I placed it here incase it is needed elsewhere.
    impl = Text


class Plugin(Base):
    __tablename__ = 'plugin'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(128), index=True)
    plugname = Column(String(128), index=True)
    stage = Column(String(15))
    link = Column(Text)
    description = Column(Text)
    repo = Column(String(10), index=True)
    versions = relationship('Version', order_by='desc(Version.date)',
                            backref='plugin', lazy='joined')
    categories = relationship('Category', secondary=catassc, backref='plugins', lazy='join')
    authors = relationship('Author', secondary=authassc, backref='plugins', lazy='join')

    def __init__(self, name, repo):
        self.name = name
        self.repo = repo

    def json(self, *fields):
        jdict = Base.json(self, *fields)
        if 'categories' in fields or len(fields) == 0:
            jdict['categories'] = [c.name for c in self.categories]
        if 'authors' in fields or len(fields) == 0:
            jdict['authors'] = [a.name for a in self.authors]
        return jdict


class Version(Base):
    __tablename__ = 'version'
    id = Column(Integer, autoincrement=True, primary_key=True)
    version = Column(String(20), index=True)
    link = Column(Text)
    download = Column(Text)
    date = Column(DateTime)
    md5 = Column(String(32))
    status = Column(String(15))
    type = Column(String(10))
    filename = Column(String(128))
    plugin_id = Column(Integer, ForeignKey('plugin.id'))
    game_versions = Column(TextPickle(pickler=json))
    permissions = Column(TextPickle(pickler=json))
    commands = Column(TextPickle(pickler=json))
    hard_dependencies = Column(TextPickle(pickler=json))
    soft_dependencies = Column(TextPickle(pickler=json))

    def __init__(self, name, plugin_id):
        self.version = name
        self.plugin_id = plugin_id


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(128), index=True)

    def __init__(self, name):
        self.name = name


class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(128), index=True)

    def __init__(self, name):
        self.name = name


class Meta(Base):
    __tablename__ = 'meta'
    id = Column(Integer, autoincrement=True, primary_key=True)
    repo = Column(String(10), index=True)
    speedy = Column(Boolean, index=True)
    duration = Column(Integer)
    timestamp = Column(Integer)
    changes = Column(TextPickle(pickler=json))

    def __init__(self, repo):
        self.repo = repo
        self.changes = []
        self.duration = 0
        self.timestamp = int(time.time())
        self.speedy = True