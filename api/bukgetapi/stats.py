import json
import bleach
import common as c
import datetime
from bottle import Bottle

app = Bottle()

@app.hook('before_request')
def set_headers():
    response.set_header('Content-Type', 'application/json')
    response.set_header('Access-Control-Allow-Origin', '*')


@app.get('/naughty_list')
def naughty_list():
    plugins = c.db.plugins.find({'_use_dbo': {'$exists': True}}, 
                                {
                                    '_id': 0,
                                    'slug': 1, 
                                    'plugin_name': 1,
                                    'authors': 1,
                                })
    return c.jsonify(plugins)


@app.get('/todays_trends')
def todays_trends():
    today = datetime.date.today().strftime('%Y-%m-%d')
    stats = c.db.stats.find({'counts.%s' % today: {'$exists': True}},
                {'_id': 0, 'slug': 1, 'server': 1, 'counts.%s' % today: 1})\
                .sort({'counts.%s' % today: -1}).limit(10)
    plugins = c.db.plugins.find({},{'slug': 1, 'versions.version': 1})
    pcount = 0
    vcount = 0
    for plugin in plugins:
        pcount += 1
        for version in plugin['versions']: vcount += 1
    return c.jsonify({
            'plugin_count': pcount,
            'version_count': vcount,
            'top_plugs': stats,
    })