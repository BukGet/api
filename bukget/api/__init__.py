import db
import common
#import v1
#import v2
import v3
import update
import stats
from bottle import Bottle, run, debug, redirect
from bukget.config import config


def start():
    app = Bottle()
    #app.mount('/1', v1.app)
    #app.mount('/2', v2.app)
    app.mount('/3', v3.app)
    app.mount('/stats', stats.app)
    app.mount('/update', update.app)

    @app.get('/')
    def home(): redirect('/3')

    @app.get('/api')
    def api1(): redirect('/3')

    @app.get('/api2')
    def api2(): redirect('/3')

    debug(config.getboolean('Settings', 'debug'))
    run(app=app,
        port=config.getint('Settings', 'port'),
        host=config.get('Settings', 'address'),
        server=config.get('Settings', 'app_server'),
        reloader=config.getboolean('Settings', 'debug')
    )