import common
import v1
import v2
import v3
import sync
import stats
from bottle import Bottle, run, debug, redirect, request


def start():
    app = Bottle()
    app.mount('/1', v1.app)
    app.mount('/2', v2.app)
    app.mount('/3', v3.app)
    app.mount('/stats', stats.app)
    app.mount('/sync', sync.app)

    # Mounted the applications for v1 and v2 on the legacy URLs as well.  It
    # appears that some apps arent handling 302 redirects all that well.
    #app.mount('/api', v1.app)
    #app.mount('/api2', v2.app)

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

    debug(common.config.getboolean('Settings', 'debug'))
    run(app=app,
        port=common.config.getint('Settings', 'port'),
        host=common.config.get('Settings', 'address'),
        server=common.config.get('Settings', 'app_server'),
        reloader=common.config.getboolean('Settings', 'debug')
    )