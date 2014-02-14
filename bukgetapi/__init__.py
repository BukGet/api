import common
import api
import sync
import stats
from bottle import Bottle, run, debug, redirect, request, ServerAdapter

def start():
    app = Bottle()
    app.mount('/3', api.app)
    app.mount('/stats', stats.app)
    app.mount('/sync', sync.app)

    @app.get('/')
    def home(): redirect('/3')

    debug(common.config.getboolean('Settings', 'debug'))
    run(app=app,
        port=common.config.getint('Settings', 'port'),
        host=common.config.get('Settings', 'address'),
        server=common.config.get('Settings', 'app_server'),
        reloader=common.config.getboolean('Settings', 'debug')
    )