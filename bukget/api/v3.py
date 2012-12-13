import json
import bleach
from bottle import Bottle, run, redirect, response, request
from bukget.api import db
from bukget.api.common import *

app = Bottle()


@app.hook('before_request')
def set_json_header():
    # We will need these set for everything in the API ;)
    response.set_header('Content-Type', 'application/json')
    response.set_header('Access-Control-Allow-Origin', '*')


@app.get('/plugins')
@app.get('/plugins/')
@app.get('/plugins/<server>')
@app.get('/plugins/<server>/')
def plugin_list(server=None):
    '''
    '''
    filters = []
    fi, fe, size, start, sort = params(request, 'slug,plugin_name,description')
    print fi, fe, size, start, sort
    if server is not None:
        server = bleach.clean(server)
        filters.append({'field': 'server', 'action': '=', 'value': server})
    return jsonify(db.plugins(filters, fi, fe, size, start, sort))




@app.get('/plugins/<server>/<slug>')
@app.get('/plugins/<server>/<slug>/')
@app.get('/plugins/<server>/<slug>/<version>')
@app.get('/plugins/<server>/<slug>/<version>/')
def plugin_details(server, slug, version=None):
    '''
    '''
    fi, fe, size, count, sort = params(request, dfexc='changelog')
    filters = [
        {'field': 'server', 'action': '=', 'value': bleach.clean(server)},
        {'field': 'slug', 'action': '=', 'value': bleach.clean(slug)}
    ]
    plugin = db.plugins(filters, fi, fe, single=True)
    if version is not None:
        if version.lower() == 'latest':
            plugin['versions'] = [plugin['versions'][0],]
        else:
            versions = plugin['versions']
            plugin['versions'] = [v for v in versions if v['version'] == version]
    return jsonify(plugin)


@app.get('/plugins/<server>/<slug>/<version>/download')
def plugin_download(server, slug, version):
    '''
    '''
    filters = [
        {'field': 'server', 'action': '=', 'value': bleach.clean(server)},
        {'field': 'slug', 'action': '=', 'value': bleach.clean(slug)}
    ]
    fields = ['versions.version', 'versions.download']
    plugin = db.plugins(filters, fields, single=True)
    if version.lower() == 'latest':
        link = [plugin['versions'][0]['download'],]
    else:
        versions = plugin['versions']
        link = [v['download'] for v in versions if v['version'] == version]
    redirect(link[0])




@app.get('/authors')
@app.get('/authors/')
def author_list():
    '''
    '''
    return jsonify(db.authors())


@app.get('/authors/<name>')
@app.get('/authors/<server>/<name>')
def author_plugins(name):
    '''
    '''
    fi, fe, size, count, sort = params(request, 'slug,plugin_name,description')
    filters = [
        {'field': 'authors', 'action': '=', 'value': bleach.clean(name)},
    ]
    if server is not None:
        server = bleach.clean(server)
        filters.append({'field': 'authors', 'action': '=', 'value': server})
    return jsonify(db.plugins(filters, fi, fe, size, count, sort))


@app.get('/categories')
@app.get('/categories/')
def category_list():
    '''
    '''
    return jsonify(db.categories())


@app.get('/categories/<name>')
@app.get('/categories/<server>/<name>')
def category_plugins(name, server=None):
    '''
    '''
    fi, fe, size, count, sort = params(request, 'slug,plugin_name,description')
    filters = [
        {'field': 'authors', 'action': '=', 'value': bleach.clean(name)},
    ]
    if server is not None:
        server = bleach.clean(server)
        filters.append({'field': 'authors', 'action': '=', 'value': server})
    return jsonify(db.plugins(filters, fi, fe, size, count, sort))


@app.post('/search')
@app.get('/search/<field>/<action>/<value>')
def search(field=None, action=None, value=None):
    '''
    '''
    fi, fe, size, count, sort = params(request, 'slug,plugin_name,description')
    filters = []
    if request.method == 'GET':
        field = bleach.clean(field)
        value = bleach.clean(value)
        filters = [
            {'field': field, 'action': action, 'value': server}
        ]
    else:
        try:
            filters = json.dumps(request.forms.get('filters'))
        except:
            raise bottle.HTTPError(404, '{"error": "invalid post"}')
    return jsonify(db.plugins(filters, fi, fe, size, count, sort))
