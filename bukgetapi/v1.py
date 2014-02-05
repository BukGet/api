import json
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
    size = c.sint(request.query.size or '')
    return c.jsonify(c.list_geninfo(size))


@app.get('/plugins')
@app.get('/plugins/')
def plugin_list():
    '''Plugin Listing
    Returns the plugin listing.  Can optionally be limited to a specific server
    binary compatability type.
    '''
    data = c.list_plugins('bukkit', ['slug',], 'slug')
    return c.jsonify([a['slug'] for a in data])


@app.get('/plugin/<slug>')
@app.get('/plugin/<slug>/')
@app.get('/plugin/<slug>/<version>')
@app.get('/plugin/<slug>/<version>/')
def plugin_details(slug, version=None):
    '''Plugin Details 
    Returns the document for a specific plugin.  Optionally can return only a
    specific version as part of the data as well.
    '''
    data = c.plugin_details('bukkit', slug, version, [])
    if not data: abort(404, "Plugin does not exist.")

    # Moving data to the old format
    data['name'] = data['slug']
    data['bukkitdev_link'] = data['dbo_page']
    data['desc'] = data['description']

    # Deleting all of the data that didnt exist in the old format.
    del(data['slug'])
    del(data['dbo_page'])
    del(data['description'])
    del(data['logo'])
    del(data['logo_full'])
    del(data['server'])
    del(data['website'])
    del(data['popularity'])
    if 'curse_link' in data: del(data['curse_link'])
    if 'curse_id' in data: del(data['curse_id'])
    if 'main' in data: del(data['main'])
    if '_use_dbo' in data: del(data['_use_dbo'])

    # Now we will perform the same actions for each version.
    versions = []
    for version in data['versions']:
        version['dl_link'] = version['download']
        version['name'] = version['version']
        del(version['commands'])
        del(version['permissions'])
        del(version['changelog'])
        del(version['md5'])
        del(version['slug'])
        del(version['download'])
        if 'file_id' in version: del(version['file_id'])
        if 'dbo_version' in version: del(version['dbo_version'])
        versions.append(version)
    data['versions'] = versions
    return c.jsonify(data)



@app.get('/plugins/<server>/<slug>/<version>/download')
def plugin_download(slug, version, server='bukkit'):
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
    return c.jsonify([a['name'] for a in c.list_authors()])


@app.get('/author/<name>')
@app.get('/author/<name>/')
def author_plugins(name, server=None):
    '''Author Plugin Listing
    Returns the plugins associated with a specific author.  Optionally can also
    be restricted to a specific server binary compatability.
    '''
    fields = ['slug',]
    start = c.sint(request.query.start or '')
    size = c.sint(request.query.size or '')
    sort = request.query.sort or 'slug'
    data = c.list_author_plugins(server, name, fields, sort)
    if size is not None and start is not None:
        return c.jsonify([a['slug'] for a in data[start:start+size]])
    return c.jsonify([a['slug'] for a in data])


@app.get('/categories')
@app.get('/categories/')
def category_list():
    '''Category Listing
    Returns the categories in the database and the number of plugins that each
    category holds.
    '''
    return c.jsonify([a['name'] for a in c.list_categories()])


@app.get('/categories/<name>')
@app.get('/categories/<name>/')
def category_plugins(name, server=None):
    '''Category Plugin listing
    returns the list of plugins that match a specific category.  Optionally a
    specific server binary compatability can be specified.
    '''
    fields = ['slug',]
    start = c.sint(request.query.start or '')
    size = c.sint(request.query.size or '')
    sort = request.query.sort or 'slug'
    data = c.list_category_plugins(server, name, fields, sort)
    if size is not None and start is not None:
        return c.jsonify([a['slug'] for a in data[start:start+size]])
    return c.jsonify([a['slug'] for a in data])


@app.post('/search')
@app.get('/search/<field>/<action>/<value>')
@app.get('/search/<field>/<action>/<value>/')
def search(field=None, action=None, value=None):
    '''Plugin search
    A generalized search system that accepts both single-criteria get requests
    as well as multi-criteria posts.
    '''
    fields = ['slug',]
    start = c.sint(request.query.start or '')
    size = c.sint(request.query.size or '')
    sort = request.query.sort or 'slug'
    field = field
    value = value
    filters = [
        {'field': field, 'action': action, 'value': value}
    ]
    try:
        data = c.plugin_search(filters, fields, sort)
    except:
        raise HTTPError(400, '{"error": "invalid search"}')
    else:
        if start is not None and size is not None:
            return c.jsonify([a['slug'] for a in data[start:start+size]])
        return c.jsonify([a['slug'] for a in data])