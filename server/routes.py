import os
import json
import re

import markdown2
from xenforo import XenForo
import bottle
from bottle import (route, template, request, default_app,
                                        redirect, static_file)
from sqlalchemy import desc

from models import NewsArticle, Repository, Session
from util import config, log, allowed_hosts

def get_from_github(filename):
    url = 'https://raw.github.com/SteveMcGrath/bukget/master/docs/%s' % filename
    markdown = markdown2.Markdown()
    raw_file = urllib2.urlopen(url).read()
    return markdown.convert(raw_file)

@route('/add', method='GET')
@route('/add', method='POST')
def add_repo():
    errors = []
    notes = []
    s = Session()

    if request.GET.get('hash','').strip():
        # If re received an activation field, then we will need to parse it out
        # and compare it to what we have on file.
        act = request.GET.get('hash','').strip()
        name = request.GET.get('plugin','').strip()
        try:
            repo = s.query(Repository).filter_by(plugin=name).one()
        except:
            errors.append('Activation Failed.  Could not find repository record.')
        else:
            if repo.hash == act:
                if not repo.manual:
                    repo.activated = True
                    s.merge(repo)
                    s.commit()
                notes.append('Activation Successful!')
                log.info('%s is now active and will be cached next generation cycle.' % name)
            else:
                errors.append('Activation Failed.  Activation Hash did not match.')

    elif request.POST.get('add','').strip():
        # If the data was posted to the page, then we need to parse out the
        # relevent data, try to match the maintainer to the one that si on the
        # bukkit forums, and lastly send an activation request.
        user = request.POST.get('user','').strip()
        url = request.POST.get('url','').strip()
        email = request.POST.get('email','').strip()
        name = request.POST.get('plugin','').strip()
        manual = bool(request.POST.get('manual','').strip())

        # Now we need to validate all the data we have to make sure it's ok before
        # continue.  First we will define the regexes that we will use to
        # validate the fields then check to make sure that they get exactly 1
        # response back from each of them.  If we don't, then we need to tell
        # the user what failed and allow them to fix their input.
        remail = re.compile(r'^[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,4}$')
        rurl = re.compile(r'^(?:http|https|ftp)\://[a-zA-Z0-9\-\./\?\=\;\%]+')
        ruser = re.compile(r'^[A-Za-z0-9\_\.\ ]+$')
        rname = re.compile(r'^[A-Za-z0-9\_]+$')

        if len(remail.findall(email)) <> 1:
            errors.append('Not a Valid Email Address.')
        if len(rurl.findall(url)) <> 1:
            errors.append('Not a Valid URL.')
        if len(ruser.findall(user)) <> 1:
            errors.append('Not a Valid Username')
        if len(rname.findall(name)) <> 1:
            errors.append('Not a Valid Plugin Name')
        if len(s.query(Repository).filter_by(plugin=name).all()) > 0:
            errors.append('Plugin Name Already Exists.')

        if len(errors) == 0:
            # If there are no errors, then we will try to activate the repository
            # that was defined.
            new_repo = Repository(name, user, email, url, manual=manual)
            if new_repo.manual:
                notes.append('Your new submission has been flagged for ' +\
                                          'manual activation.  Please work with our staff in ' +\
                                          'the IRC channel to get your plugin activated.')
                s.add(new_repo)
                s.commit()
            else:
                if new_repo.activate():
                    notes.append('Please check your Bukkit.org account for ' +\
                                              'activation message.  If you havent received one, ' +\
                                              'please contact us.')
                    s.add(new_repo)
                    s.commit()
                else:
                    errors.append('We were unable to send your Bukkit.org account the ' +\
                                                'activation message.  If this issue continues please '+\
                                                'notify us of the issue.')
    s.close()
    return template('page_add', notes=notes, errors=errors)

#@route('/')
#def home_page():
#  return template('page_home')

@route('/')
@route('/news')
def news_page():
    s = Session()
    news = s.query(NewsArticle).order_by(desc(NewsArticle.date)).all()
    s.close()
    return template('page_news', news=news)

@route('/repo')
@route('/repo/')
@route('/repo/#.+#')
@route('/repo#.+#')
def repo_page():
    return template('page_repo')

@route('/log')
def display_logs():
    logfile = open(config.get('Settings', 'log_file'), 'r')
    logdata = logfile.read()
    logfile.close()
    return template('page_logs', logdata=logdata, ENV=ENV)

@route('/code')
def github_redirect():
    redirect('https://github.com/SteveMcGrath/bukget')

@route('/about')
def about_us():
    return template('page_about')

@route('/repo.json')
def get_repo_file():
    return static_file('repo.json', config.get('Settings','static_files'))

@route('/favicon.ico')
def get_repo_file():
    return static_file('images/favicon.ico', config.get('Settings','static_files'))

@route('/help')
def help_page():
    return template('page_markdown', data=get_from_github('help.md'), title='Help')

@route('/plugins')
def search_page():
    return template('page_plugins')

@route('/static/:filename#.+#')
def route_static_files(filename):
    return static_file(filename, root=config.get('Settings', 'static_files'))

@route('/baskit')
def baskit_page():
    return template('page_baskit')

@route('/burt')
def burt_page():
    return template('page_burt')

@route('/baskit/download')
def baskit_download():
    redirect('https://raw.github.com/SteveMcGrath/baskit/master/baskit.py')

@route('/generate')
def generate_repository():
    '''
    Generates the master repository file.
    '''
    if request.environ.get('REMOTE_ADDR') in allowed_hosts:
        #log.info('Running Generation Cycle.')
        s = Session()
        rdict = []
        repos = s.query(Repository).filter_by(activated=True).all()
        for repo in repos:
            if repo.update():
                s.merge(repo)
                s.commit()
            if repo.cache is not None:
                rdict.append(json.loads(repo.cache))
        rfile = open(os.path.join(\
                                  config.get('Settings', 'static_files'),'repo.json'), 'w')
        rfile.write(json.dumps(rdict))
        rfile.close()
        s.close()
        return '{"plugins": %s}' % len(repos)
    return '{"error": "Not an allowed address"}'
