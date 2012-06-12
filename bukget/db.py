import json
import bukget.config
from sqlalchemy import (Table, Column, Integer, ForeignKey, PickleType, Text,
						and_, desc, create_engine)
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base



DBase = declarative_base()

# This is the on-disk database
disk = create_engine(bukget.conf.get('Settings', 'db_string'))
Session = sessionmaker(disk)

# This is the in-memory database
memory = create_engine('sqlite://:memory:')
Reactor = sessionmaker(memory)


def initialize(engine):
	Plugin.metadata.create_all(engine)
	Version.metadata.create_all(engine)
	Repo.metadata.create_all(engine)
	Category.metadata.create_all(engine)
	Author.metadata.create_all(engine)
	catassc.create(engine)
	authassc.create(engine)


def clear(engine):
    '''clear enigine
    This function will drop all of the dables in a database, effectively
    clearing out the database for re-initialization.
    '''
    meta = MetaData(engine)
    meta.reflect()
    meta.drop_all()


def _migrate(s, d, table):
    rows = s.query(table).all()

    for row in rows:
        s.expunge(row)
        d.merge(row)
    d.commit()


def clone(source, dest):
	'''clone source dest
	This function will completely clone the Database from the source engine to
	the destination engine.  This is very useful for replicating information
	in and out of memory as we will be primarially using an in-memory sqlite
	database for BukGet for performance purposes.
	'''
    # First we need to scrub and initialize the destination to make sure that it
    # is primed for us to work our magic ;)
    clear(dest)
    init(dest)

    # Next we need to setup the session reactors and build the sessions that we
    # will be working with.
    smaker = sessionmaker(source)
    dmaker = sessionmaker(dest)

    s = smaker()
    d = dmaker()

    # Now for the actual work, We will run migrate on each table we want to
    # replicate.
    _migrate(s, d, Plugin)
    _migrate(s, d, Version)
    _migrate(s, d, Repo)
    _migrate(s, d, Category)
    _migrate(s, d, Author)
    _migrate(s, d, Meta)
    _migrate(s, d, catassc)
    _migrate(s, d, authassc)

    # Lastly we need to close out the sessions.
    s.close()
    d.close()


def replace(engine):
    '''replace engine
    This function is designed to very simply clone the database engine given to
    us, and return with the sqlite in-memory engine.  This is especially useful
    for startup and for the updates, as all of the changes can be done to an
    in-memory copy and then once everything is complete a new, pristine database
    is returned to the application.
    '''
    mem2 = create_engine('sqlite://:memory:')
    clone(engine, mem2)
    return mem2, sessionmaker(mem2)


class Base(DBase):
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
		if len(fields) == 0:
			for field in fields:
				jdict[field] = self.__dict__[field]
				# Some code will have to be added here to account for
				# relationship models, however I will have to run some
				# tests first.
		else:
			jdict = self.__dict__
		return jdict


class TextPickle(PickleType):
	# This is a simple overloaded pickler type so that we can embed JSON
	# into the database if needed.  This is mostly used with the Version
	# table, however I placed it here incase it is needed elsewhere.
	impl = Text


# The Category Association Table.  This table houses the relationships
# between plugins and categories.
catassc = Table('catagory_associations', DBase.metadata,
	Column('plugin_id', Integer, ForeignKey('plugin.id')),
	Column('category_id', Integer, ForeignKey('category.id'))
)


# The Author Association Table.  This table houses the relationships
# between authors and plugins.
authassc = Table('author_association', DBase.metadata,
	Column('author_id', Integer, ForeignKey('author.id')),
	Column('plugin_id', Integer, ForeignKey('plugin_id'))
)


class Plugin(Base):
	__tablename__ = 'plugin'
	id = Column(Integer, auto_ncrement=True, primary_key=True)
	name = Column(String)
	plugname = Column(String)
	status = Column(String)
	link = Column(Text)
	description = Column(Text)
	repo_id = Column(Integer, ForeignKey('repo.id'))
	repo = relationship('Repo', backref='plugins')
	versions = relationship('Version', order_by='desc(Version.date)',
							backref='plugin')
	categories = relationship('Category', secondary=catassc, backref='plugins')
	authors = relationship('Author', secondary=authassc, backref='plugins')


class Version(Base):
	__tablename__ = 'version'
	id = Column(Integer, auto_increment=True, primary_key=True)
	version = Column(String)
	link = Column(String)
	download = Column(String)
	date = Column(DateTime)
	md5 = Column(String)
	status = Column(String)
	type = Column(String)
	plugin_id = Column(Integer, ForeignKey('plugin.id'))
	permissions = Column(TextPickle(pickler=json))
	commands = Column(TextPickle(pickler=json))
	hard_dependencies = Column(TextPickle(pickler=json))
	soft_dependencies = Column(TextPickle(pickler=json))


class Repo(Base):
	__tablename__ = 'repo'
	id = Column(Integer, auto_increment=True, primary_key=True)
	name = Column(String)


class Category(Base):
	__tablename__ = 'category'
	id = Column(Integer, auto_increment=True, primary_key=True)
	name = Column(String)


class Author(Base):
	__tablename__ = 'author'
	id = Column(Integer, auto_increment=True, primary_key=True)
	name = Column(String)


