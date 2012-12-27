import common
import v1
import v2
import v3
import update
import stats
from bottle import Bottle, run, debug, redirect, request
from ConfigParser import ConfigParser

config = ConfigParser()
config.read('/etc/bukget/bukget.conf')

def start():
    app = Bottle()
    app.mount('/1', v1.app)
    app.mount('/2', v2.app)
    app.mount('/3', v3.app)
    app.mount('/stats', stats.app)
    app.mount('/sync', sync.app)

    @app.get('/')
    def home(): redirect('/3')

    @app.get('/api')
    @app.get('/api/')
    @app.get('/api/<path:re:(.*)>')
    def api1(path=''): redirect('/1/%s?%s' % (path, request.query_string))

    @app.get('/api2')
    @app.get('/api2/')
    @app.get('/api2/<path:re:(.*)>')
    def api2(path=''): redirect('/2/%s?%s' % (path, request.query_string))

    debug(config.getboolean('Settings', 'debug'))
    run(app=app,
        port=config.getint('Settings', 'port'),
        host=config.get('Settings', 'address'),
        server=config.get('Settings', 'app_server'),
        reloader=config.getboolean('Settings', 'debug')
    )