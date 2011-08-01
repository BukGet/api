#!/usr/bin/env python
from models import Session, NewsArticle
import datetime

def getdate(s):
    year, month, day = s.split()[0].split('-')
    hour, minute = s.split()[1].split(':')
    return datetime.datetime(int(year), int(month), int(day),
                                                      int(hour), int(minute))

session = Session()
article = open('article.md').read()
title = article.split('\n')[0]
date = getdate(article.split('\n')[1])
post = '\n'.join(article.split('\n')[2:])
news = NewsArticle(title, post)
session.add(news)
session.commit()
session.close()
