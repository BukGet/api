#!/usr/bin/env python
import os
from ConfigParser import ConfigParser

#### CONFIGURATION AND PRE-PROCESSING
# The script has to run from the location on disk that it lives.
os.chdir(os.path.dirname(__file__))

config = ConfigParser()
config.read('bukget.ini')

# Activate the virtualenv
if config.getboolean('Settings', 'virtual_env'):
    activate_this = '../bin/activate_this.py'
    execfile(activate_this, dict(__file__=activate_this))

import bukget
import markdown2
from bottle import redirect, debug, Bottle, run, static_file, template

app = Bottle()
app.mount('/api', bukget.webapi.app)

def page(name):
    pfile = open(os.path.join('content', '%s.md' % name))
    mdpage = pfile.read()
    pfile.close()
    md = markdown2.Markdown()
    return md.convert(mdpage)

@app.route('/api')
def api_redir():
    redirect('/api/')

@app.route('/blog')
@app.route('/repo')
@app.route('/')
def main_page():
    return template('layout', content=page('home_page'))

@app.route('/baskit')
def baskit_page():
    return template('layout', content=page('baskit'))

@app.route('/static/:filename#.+#')
def route_static_files(filename):
    return static_file(filename, root='static')

@app.route('/favicon.ico')
def get_repo_file():
    return static_file('images/favicon.ico', 'static')
    
if __name__ == '__main__':
    debug(config.getboolean('Settings', 'debug'))
    bukget.webapi.update_cache()
    run(app=app, 
        port=config.get('Settings', 'port'), 
        host=config.get('Settings', 'host'), 
        server=config.get('Settings', 'server'), 
        reloader=config.getboolean('Settings', 'debug'))