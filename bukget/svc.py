import multiprocessing
import markdown
import bottle
from bukget.config import config
import bukget.api
import bukget.db
import time
from urllib2 import urlopen
from log import log
from sqlalchemy import desc
import bukget.parsers


def website():
    initialize()
    app = bottle.Bottle()
    if config.getboolean('Settings', 'enable_api'):
        app.mount('/api', bukget.legacy.app)
        app.mount('/api2', bukget.api.app)
    if config.getboolean('Settings', 'enable_site'):

        @app.route('/')
        def home_page():
            url = 'https://raw.github.com/SteveMcGrath/bukget/master/README.md'
            page = urlopen(url).read()
            return markdown.markdown(page)

    bottle.debug(config.getboolean('Settings', 'debug'))
    bottle.run(app=app,
               port=config.get('Settings', 'port'),
               host=config.get('Settings', 'host'),
               server=config.get('Settings', 'server'),
               reloader=config.getboolean('Settings', 'debug'))


def updater():
    initialize()
    parsers = []
    while True:
        log.debug('Running Update Check')
        for parser in config.get('Settings', 'parsers').split():
            log.debug('Checking if %s needs to be updated' % parser)
            s = bukget.db.Session()
            meta = s.query(bukget.db.Meta).filter_by(repo=parser)\
                    .order_by(desc(bukget.db.Meta.id)).first()
            s.close()
            delay = int(time.time() - meta.timestamp)
            log.debug('%s update delay is currently %s of %s' % (parser, 
                      delay, config.get(parser, 'update_delay')))
            if delay >= config.getint(parser, 'update_delay'):
                p = bukget.parsers.parsers[parser]()
                p.start()
                parsers.append(p)
        for parser in parsers:
            if not parser.isAlive():
                del parsers[parsers.index(parser)]
                log.debug('Removed Completed Parser %s' % parser.ident)
        log.debug('Active Parsers: %s' % len(parsers))
        time.sleep(30)



def initialize():
    bukget.db.init(bukget.db.disk)
    s = bukget.db.Session()
    for parser in config.get('Settings', 'parsers').split():
        meta = s.query(bukget.db.Meta).filter_by(repo=parser)\
                .order_by(desc(bukget.db.Meta.id)).first()
        if meta == None:
            newmeta = bukget.db.Meta(parser)
            newmeta.timestamp = 0
            s.add(newmeta)
            s.commit()