#!/usr/bin/env python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Table, Column, Integer, String, DateTime, Date, 
                        ForeignKey, Text, Boolean, create_engine, MetaData, 
                        and_, desc)
from sqlalchemy.orm import relationship, backref, sessionmaker
from ConfigParser import ConfigParser
import datetime

config = ConfigParser()
config.read('config.ini')
Base = declarative_base()

class NewsArticle(Base):
  '''
  News article class for the site.
  '''
  __tablename__ = 'news'
  id    = Column(Integer(8), primary_key=True)
  title = Column(String(128))
  date  = Column(DateTime)
  data  = Column(Text)
  
  def __init__(self, title, post, date=None):
    if date is not None:
      self.date = date
    else:
      self.date = datetime.datetime.now()
    self.title = title
    self.data = post
  
  def get_html(self):
    markdown = markdown2.Markdown()
    return markdown.convert(self.data)

def getdate(s):
  year, month, day = s.split()[0].split('-')
  hour, minute = s.split()[1].split(':')
  return datetime.datetime(int(year), int(month), int(day), 
                           int(hour), int(minute))
  

engine = create_engine(config.get('Settings', 'db_string'))
Session = sessionmaker(bind=engine)
NewsArticle.metadata.create_all(engine)
session = Session()
article = open('article.md').read()
title = article.split('\n')[0]
date = getdate(article.split('\n')[1])
post = '\n'.join(article.split('\n')[2:])
news = NewsArticle(title, post)
session.add(news)
session.commit()
session.close()