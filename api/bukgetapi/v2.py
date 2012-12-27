import json
import bleach
from bottle import Bottle, run, redirect, response, request
import common as c

app = Bottle()


def v2to3(items):
    convert = {
        'plugname': 'plugin_name',
        'name': 'slug',
        'repo': 'server',
        'link': 'dbo_page',
        'slug': 'name',
    }
    data = []
    for item in items:
        if item in convert:
            data.append(convert[item])
        else:
            data.append(item)
    return data


def v3to2(items):
    data = []
    for item in items:
        if 'dbo_page' in item:
            item['link'] = item['dbo_page']
            del(item['dbo_page'])
        if 'server' in item:
            item['repo'] = item['server']
            del(item['server'])
        if 'plugin_name' in item:
            item['plugname'] = item['plugin_name']
            del(item['plugin_name'])
        if 'slug' in item:
            item['name'] = item['slug']
            del(item['slug'])
        if 'logo' in item: del(item['logo'])
        if 'logo_full' in item: del(item['logo_full'])
        if 'versions' in item:
            versions = []
            for version in item['versions']:
                if 'slug' in version: del(item['slug'])
                if 'changelog' in version: del(item['changelog'])
            item['versions'] = versions
        data.append(item)
    return data        


@app.hook('before_request')
def set_json_header():
    # We will need these set for everything in the API ;)
    response.set_header('Content-Type', 'application/json')
    response.set_header('Access-Control-Allow-Origin', '*')


@app.get('/')
@app.get('/geninfo')
@app.get('/geninfo/')
def generation_info():
    '''Generation Information
    Returns the generation information as requested.  User can optionall request
    to look X number of versions back.
    '''
    size = c.sint(bleach.clean(request.query.size or None))
    return c.jsonify(c.list_geninfo(size))


@app.get('/<server>/plugins')
@app.get('/<server>/plugins/')
def plugin_list(server=None):
    '''Plugin Listing
    Returns the plugin listing.  Can optionally be limited to a specific server
    binary compatability type.
    '''
    fields = bleach.clean(request.query.fields or 'slug,plugin_name,description').split(',')
    fields = v2to3(fields)
    start = c.sint(bleach.clean(request.query.start or None))
    size = c.sint(bleach.clean(request.query.size or None))
    sort = bleach.clean(request.query.sort or 'slug')
    data = c.list_plugins(server, fields, sort)
    if size is not None and start is not None:
        return c.jsonify(v3to2(data[start:start+size]))
    return c.jsonify(v3to2(data))


@app.get('/<server>/plugin/<slug>')
@app.get('/<server>/plugin/<slug>/')
@app.get('/<server>/plugin/<slug>/<version>')
@app.get('/<server>/plugin/<slug>/<version>/')
def plugin_details(server, slug, version=None):
    '''Plugin Details 
    Returns the document for a specific plugin.  Optionally can return only a
    specific version as part of the data as well.
    '''
    fields = bleach.clean(request.query.fields or '').split(',')
    fields = v2to3(fields)
    data = c.plugin_details(server, slug, version, fields)
    return c.jsonify(v3to2([data])[0])




@app.get('/<server>/plugin/<slug>/<version>/download')
def plugin_download(server, slug, version):
    '''Plugin Download Redirector
    Will attempt to redirect to the plugin download for the version specified.
    If no version exists, then it will throw a 404 error.
    '''
    plugin = c.plugin_details(server, slug, version, {})
    if version.lower() == 'latest':
        link = [plugin['versions'][0]['download'],]
    else:
        versions = plugin['versions']
        link = [v['download'] for v in versions if v['version'] == version]
    if len(link) > 0:
        redirect(link[0])
    else:
        raise bottle.HTTPError(404, '{"error": "could not find version"}')


@app.get('/authors')
@app.get('/authors/')
def author_list():
    '''Author Listing
    Returns a full listing of the authors in the system and the number of
    plugins that they have in the database.
    '''
    return c.jsonify([a['name'] for a in c.list_authors()])


@app.get('/<server>/author/<name>')
@app.get('/<server>/author/<name>/')
def author_plugins(server, name):
    '''Author Plugin Listing
    Returns the plugins associated with a specific author.  Optionally can also
    be restricted to a specific server binary compatability.
    '''
    fields = bleach.clean(request.query.fields or 'name,plugname,description').split(',')
    fields = v2to3(fields)
    start = c.sint(bleach.clean(request.query.start or None))
    size = c.sint(bleach.clean(request.query.size or None))
    sort = bleach.clean(request.query.sort or 'slug')
    data = c.list_author_plugins(server, name, fields, sort)
    if size is not None and start is not None:
        return c.jsonify(v3to2(data[start:start+size]))
    return c.jsonify(v3to2(data))


@app.get('/categories')
@app.get('/categories/')
def category_list():
    '''Category Listing
    Returns the categories in the database and the number of plugins that each
    category holds.
    '''
    return c.jsonify([a['name'] for a in c.list_categories()])


@app.get('/<server>/category/<name>')
@app.get('/<server>/category/<name>/')
def category_plugins(server, name):
    '''Category Plugin listing
    returns the list of plugins that match a specific category.  Optionally a
    specific server binary compatability can be specified.
    '''
    fields = bleach.clean(request.query.fields or 'name,plugname,description').split(',')
    fields = v2to3(fields)
    start = c.sint(bleach.clean(request.query.start or None))
    size = c.sint(bleach.clean(request.query.size or None))
    sort = bleach.clean(request.query.sort or 'slug')
    data = c.list_category_plugins(server, name, fields, sort)
    if size is not None and start is not None:
        return c.jsonify(v3to2(data[start:start+size]))
    return c.jsonify(v3to2(data))


@app.get('/search/<base>/<field>/<action>/<value>')
@app.get('/search/<base>/<field>/<action>/<value>/')
def search(base=None, field=None, action=None, value=None):
    '''Plugin search
    A generalized search system that accepts both single-criteria get requests
    as well as multi-criteria posts.
    '''
    fields = bleach.clean(request.query.fields or 'name,plugname,description').split(',')
    fields = v2to3(fields)
    start = c.sint(bleach.clean(request.query.start or None))
    size = c.sint(bleach.clean(request.query.size or None))
    sort = bleach.clean(request.query.sort or 'slug')
    field = bleach.clean(field)
    value = bleach.clean(value)
    base = bleach.clean(base)
    if base == 'version':
        field = 'versions.%s' % field
    filters = [
        {'field': field, 'action': action, 'value': value}
    ]
    try:
        data = c.plugin_search(filters, fields, sort)
    except:
        raise bottle.HTTPError(400, '{"error": "invalid search"}')
    else:
        if start is not None and size is not None:
            return c.jsonify(v3to2(data[start:start+size]))
        return c.jsonify(v3to2(data))
