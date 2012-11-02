import multiprocessing
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
    '''
    Web API startup function
    '''

    # First thing we need to do is initialize the database incase it's clean or
    # if there are any needed changes.
    initialize()

    # Next we will built an empty bottle container.
    app = bottle.Bottle()

    # Next we will bootstrap in the API(s).
    app.mount('/api', bukget.legacy.app)
    app.mount('/api2', bukget.api.app)

    # Lastly we setup a redirect to the main site if someone goes directly to
    # the root URI.
    @app.route('/')
    def home_page():
        bottle.redirect('http://bukget.org')

    # Do we want debugging turned on?
    bottle.debug(config.getboolean('Settings', 'debug'))

    # Startup the web service...
    bottle.run(app=app,
               port=config.get('Settings', 'port'),
               host=config.get('Settings', 'host'),
               server=config.get('Settings', 'server'),
               reloader=config.getboolean('Settings', 'debug'))


def updater():
    '''
    BukGet Database updater
    '''

    # First thing we need to do is initialize the database incase it's clean or
    # if there are any needed changes.
    initialize()

    # Now for some initialization stuff:
    parsers = []    # The running parser array.  When we spawn a new parser,
                    # it will reside here.

    while True:
        # Here we will be performing the update check.  This is scheduled to
        # happen every 30 seconds for all of the parsers.
        log.debug('Running Update Check')
        for parser in config.get('Settings', 'parsers').split():
            log.debug('Checking if %s needs to be updated' % parser)

            # The first thing we need to do here is to query the database for
            # the last full and speedy generations, then compute how many
            # seconds have elapsed since they were last run.
            s = bukget.db.Session()
            meta = s.query(bukget.db.Meta)\
                    .filter_by(repo=parser)\
                    .order_by(desc(bukget.db.Meta.id)).first()
            fmeta = s.query(bukget.db.Meta)\
                     .filter_by(repo=parser, speedy=False)\
                     .order_by(desc(bukget.db.Meta.id)).first()
            delay = int(time.time() - meta.timestamp)
            fdelay = int(time.time() - fmeta.timestamp)
            s.close()


            # Lets go ahead and log those times to the dubug messages...
            log.debug('%s sDelay=%s/%s fDelay=%s/%s' % (parser, 
                      delay, config.get(parser, 'speedy_delay'),
                      fdelay, config.get(parser, 'full_delay')))

            # Now we will check first the full delay, then the speedy delay
            # depending on our needs.
            if fdelay >= config.getint(parser, 'full_delay'):
                p = bukget.parsers.parsers[parser](speedy=False)
                p.start()
                parsers.append(p)
            elif delay >= config.getint(parser, 'speedy_delay'):
                p = bukget.parsers.parsers[parser]()
                p.start()
                parsers.append(p)

        # Lastly is cleanup.  We will check to see if any parsers have finished
        # and clean them up in the parser list.
        for parser in parsers:
            if not parser.isAlive():
                del parsers[parsers.index(parser)]
                log.debug('Removed Completed Parser %s' % parser.ident)
        log.debug('Active Parsers: %s' % len(parsers))
        time.sleep(30)  # our sleep delay ;)



def initialize():
    '''Database Initialization function
    This should be run before doing anything with BukGet, as it preps a clean
    database for all the parsers configured.
    '''
    bukget.db.init(bukget.db.disk)  # Initialize the database and
    s = bukget.db.Session()         # start up a session.
    for parser in config.get('Settings', 'parsers').split():

        # Here we will check to see if any metadata for the parser exists.  If
        # there isn't any rows, then we will go ahead and create one.
        meta = s.query(bukget.db.Meta).filter_by(repo=parser)\
                .order_by(desc(bukget.db.Meta.id)).first()
        if meta == None:
            newmeta = bukget.db.Meta(parser)
            newmeta.timestamp = 0
            newmeta.speedy = False
            s.add(newmeta)
            s.commit()
    s.close()