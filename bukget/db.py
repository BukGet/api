import json
import bukget.config
from sqlalchemy import (Table, Column, Integer, ForeignKey, PickleType, Text,
						and_, desc, create_engine)
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


DBase = declarative_base()
engine = create_engine(bukget.conf.get('Settings', 'db_string'))
Session = sessionmaker(engine)


def initialize():
	Plugin.metadata.create_all(engine)
	Version.metadata.create_all(engine)
	Repo.metadata.create_all(engine)
	Category.metadata.create_all(engine)
	Author.metadata.create_all(engine)
	catassc.create(engine)
	authassc.create(engine)


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
	date = Column(DateTime)
	supports = Column(TextPickle(pickler=json))
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


