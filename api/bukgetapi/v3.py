import json
import bleach
from bottle import Bottle, redirect, response, request, abort, HTTPError
import common as c

app = Bottle()


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
    size = c.sint(request.query.size or None)
    callback = request.query.callback or None
    return c.jsonify(c.list_geninfo(size), callback)


@app.get('/geninfo/<idnum>')
def get_geninfo(idnum):
    '''Specific Generation Information
    Return information on a specific generation.
    '''
    callback = request.query.callback or None
    return c.jsonify(c.get_geninfo(idnum), callback)


@app.get('/plugins')
@app.get('/plugins/')
@app.get('/plugins/<server>')
@app.get('/plugins/<server>/')
def plugin_list(server=None):
    '''Plugin Listing
    Returns the plugin listing.  Can optionally be limited to a specific server
    binary compatability type.
    '''
    fields = (request.query.fields or 'slug,plugin_name,description').split(',')
    start = c.sint(request.query.start or None)
    size = c.sint(request.query.size or None)
    sort = request.query.sort or 'slug'
    callback = request.query.callback or None
    data = c.list_plugins(server, fields, sort, start, size)
    return c.jsonify(data, callback)


@app.get('/plugins/<server>/<slug>')
@app.get('/plugins/<server>/<slug>/')
@app.get('/plugins/<server>/<slug>/<version>')
@app.get('/plugins/<server>/<slug>/<version>/')
def plugin_details(server, slug, version=None):
    '''Plugin Details 
    Returns the document for a specific plugin.  Optionally can return only a
    specific version as part of the data as well.
    '''
    fields = (request.query.fields or '').split(',')
    size = c.sint(request.query.size or None)
    data = c.plugin_details(server, slug, version, fields)
    if not data: abort(404, "Plugin Does Not Exist")
    callback = request.query.callback or None
    if size is not None:
        data['versions'] = data['versions'][:size]
    return c.jsonify(data, callback)


@app.get('/plugins/<server>/<slug>/<version>/download')
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
        raise HTTPError(404, '{"error": "could not find version"}')


@app.get('/authors')
@app.get('/authors/')
def author_list():
    '''Author Listing
    Returns a full listing of the authors in the system and the number of
    plugins that they have in the database.
    '''
    callback = request.query.callback or None
    return c.jsonify(c.list_authors(), callback)


@app.get('/authors/<name>')
@app.get('/authors/<name>/')
@app.get('/authors/<server>/<name>')
@app.get('/authors/<server>/<name>/')
def author_plugins(name, server=None):
    '''Author Plugin Listing
    Returns the plugins associated with a specific author.  Optionally can also
    be restricted to a specific server binary compatability.
    '''
    callback = request.query.callback or None
    fields = (request.query.fields or 'slug,plugin_name,description').split(',')
    start = c.sint(request.query.start or None)
    size = c.sint(request.query.size or None)
    sort = request.query.sort or 'slug'
    data = c.list_author_plugins(server, name, fields, sort, start, size)
    return c.jsonify(data, callback)


@app.get('/categories')
@app.get('/categories/')
def category_list():
    '''Category Listing
    Returns the categories in the database and the number of plugins that each
    category holds.
    '''
    callback = request.query.callback or None
    return c.jsonify(c.list_categories(), callback)


@app.get('/categories/<name>')
@app.get('/categories/<name>/')
@app.get('/categories/<server>/<name>')
@app.get('/categories/<server>/<name>/')
def category_plugins(name, server=None):
    '''Category Plugin listing
    returns the list of plugins that match a specific category.  Optionally a
    specific server binary compatability can be specified.
    '''
    callback = request.query.callback or None
    fields = (request.query.fields or 'slug,plugin_name,description').split(',')
    start = c.sint(request.query.start or None)
    size = c.sint(request.query.size or None)
    sort = request.query.sort or 'slug'
    data = c.list_category_plugins(server, name, fields, sort, start, size)
    return c.jsonify(data, callback)


@app.post('/updates')
def get_updates():
    '''Plugin updates
    Returns a list of dictionaries with the latest, release, beta, and alpha
    version numbers.
    '''
    callback = request.forms.get('callback') or None
    slugs = (request.forms.get('slugs') or '').split(',')
    server = request.forms.get('server') or 'bukkit'
    try:
        data = c.plugins_up_to_date(slugs, server)
    except:
        raise HTTPError(400, '{"error": "invalid post"}')
    else:
        return c.jsonify(data, callback)


@app.post('/search')
@app.get('/search/<field>/<action>/<value>')
@app.get('/search/<field>/<action>/<value>/')
def search(field=None, action=None, value=None):
    '''Plugin search
    A generalized search system that accepts both single-criteria get requests
    as well as multi-criteria posts.
    '''
    filters = []
    if request.method == 'GET':
        callback = request.query.callback or None
        fields = (request.query.fields or 'slug,plugin_name,description').split(',')
        start = c.sint(request.query.start or None)
        size = c.sint(request.query.size or None)
        sort = request.query.sort or 'slug'
        field = field
        value = value
        filters = [
            {'field': field, 'action': action, 'value': value}
        ]
    else:
        callback = request.forms.get('callback') or None
        filters = json.loads(request.forms.get('filters') or '[]'
        fields = (request.forms.get('fields')) or 'slug,plugin_name,description').split(',')
        start = c.sint(request.forms.get('start') or None
        size = c.sint(request.forms.get('size') or None
        sort = request.forms.get('sort') or 'slug'
    try:
        data = c.plugin_search(filters, fields, sort, start, size)
    except:
        raise HTTPError(400, '{"error": "invalid post"}')
    else:
        return c.jsonify(data, callback)
