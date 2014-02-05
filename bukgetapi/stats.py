import json
import bleach
import common as c
import datetime
from bottle import Bottle, redirect, response, request

app = Bottle()

@app.hook('before_request')
def set_json_header():
    response.set_header('Content-Type', 'application/json')
    response.set_header('Access-Control-Allow-Origin', '*')


@app.get('/naughty_list')
def naughty_list():
    callback = bleach.clean(request.query.callback or None)
    plugins = list(c.db.plugins.find({'_use_dbo': {'$exists': True}}, 
                                {
                                    '_id': 0,
                                    'slug': 1, 
                                    'plugin_name': 1,
                                    'authors': 1,
                                }))
    return c.jsonify(plugins, callback)


@app.get('/todays_trends')
def todays_trends():
    callback = bleach.clean(request.query.callback or None)
    plugins = c.db.plugins.find({},{'slug': 1, 'versions.version': 1})
    pcount = 0
    vcount = 0
    for plugin in plugins:
        pcount += 1
        for version in plugin['versions']: vcount += 1
    return c.jsonify({
            'plugin_count': pcount,
            'version_count': vcount,
    }, callback)


@app.get('/trend/<days:int>')
@app.get('/trend/<days:int>/<names>')
def plugin_trends(days, names=None):
    fields = {'_id': 0}
    if names == None: 
        fields['plugins'] = 0
    else:
        for name in bleach.clean(names).split(','):
            fields['plugins.%s' % name] = 1
        fields['timestamp'] = 1
    callback = bleach.clean(request.query.callback or None)
    trends = list(c.db.webstats.find({}, fields).sort('_id', -1).limit(days))
    return c.jsonify(trends, callback)

