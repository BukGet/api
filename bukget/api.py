from bottle import Bottle, request, response, template, redirect, error
from sqlalchemy import desc, and_, or_
from sqlalchemy.orm import joinedload
from bottle.ext import sqlalchemy
from bukget.config import config
from bukget.log import log
import bleach
import bukget.db as db
import json

app = Bottle()
app.install(sqlalchemy.Plugin(db.disk, db.Base.metadata, keyword='s'))

def jsonify(dataset):
    # This is an abstraction of json.dumps incase we need to augment it
    # for any reason.
    return json.dumps(dataset)


def raw_sql(query, request, session, fields, start=None, size=None):
    '''raw_sql query request_object, session_object
    This function is designed to be a central point where we can send queries
    and get formatted JSON data back.  As we have several functions that will
    be relying on raw queries for speed purposes, it made sence to centralize
    this here.
    '''

    # Here we will be running the query.  You can see that we are
    # running a raw SQL query here and now going through the ORM.
    # This is mainly because of the issues with overhead of the
    # SQLAlchemy ORM and larger datasets.
    rows = session.execute(query)

    # Now we are gonna parse and jsonify the dataset that we got
    # back.  There is a little bit of hackery here for pagination as
    # well.  We are still pulling back the full dataset, and then just
    # parsing out the subset we need.  This is done this way so that
    # we can still alphabatize the dataset but still gain pagination.
    # I'm sure there is a more efficient way to handle this, however I'm
    # not a competent enough DBA to figure it out.
    plist = []
    fields = [f.split('.')[-1] for f in fields]

    for plugin in rows:
        # Build the JSON Row.
        item = {}
        for field in fields:
            item[field] = plugin[field]
        plist.append(item)
    rows.close()
    return plist


@app.hook('before_request')
def set_json_header():
    # We will need this set for everything in the API ;)
    response.set_header('Content-Type', 'application/json')
    response.set_header('Access-Control-Allow-Origin', '*')


@error(404)
@error(500)
def error404(error):
    return jsonify({'ERROR': 'Bad Request'})

@app.route('/')
def metadata(s):
    # Here we query for the last row in the Meta table, and jsonify it
    # before returning it to the user.
    meta = s.query(db.Meta).order_by(desc(db.Meta.id)).first()
    return jsonify(meta.json())


@app.route('/<repo>/plugins')
def plugin_list(repo, s, convert=True):
    # First we need to initialize everything
    start = request.query.start or 0
    size = request.query.size or -1
    fstring = request.query.fields or 'name,plugname,description'
    sort = request.query.sort or 'name'
    
    # For the data that were were accepting input, lets go
    # ahead and sanatize the input of any potential evil ;)
    fields = bleach.clean(fstring).split(',')
    repo = bleach.clean(repo)
    start = int(bleach.clean(start))
    size = int(bleach.clean(size))
    sort = bleach.clean(sort)

    # This is the query that we will be sending on to raw_sql
    # for processing.
    query = 'SELECT %s FROM plugin WHERE repo = \'%s\' ORDER BY %s' %\
            (','.join(fields), repo, sort)

    if size > 0:
        query += ' LIMIT %d, %d' % (start, size)

    # And now we hand off all of the fun bits to raw_sql ;)
    data = raw_sql(query, request, s, fields, start, size)
    if convert:
        return jsonify(data)
    else:
        return data


@app.route('/<repo>/plugin/<name>')
def plugin_details(repo, name, s):
    # This query will pull all of the information related to this
    # specific plugin, then jsonify all of the information and
    # return it as part of the API.
    plugin = s.query(db.Plugin).filter_by(name=name, repo=repo)\
                               .options(joinedload('categories'),
                                        joinedload('authors')).first()
    if plugin is None:
        return jsonify({'error': 'Plugin %s does not exist' % name})
    pdata = plugin.json()
    return jsonify(pdata)


@app.route('/<repo>/plugin/<name>/<version>')
def plugin_version(repo, name, version, s):
    # Here we are only returning the verion information for a specific
    # version of this plugin.  Again this is a bit hackish and I'm sure there 
    # is a way to do this within SQLAlchemy.  I should probably have someone 
    # who knows what they are looking at look through this code ;)
    plugin = s.query(db.Plugin).filter_by(name=name, repo=repo)\
                               .options(joinedload('categories'),
                                        joinedload('authors')).first()

    if plugin is None:
        return jsonify({'error': 'Plugin %s does not exist' % name})

    vobj = None
    if version == 'latest':
        # If the version is latest, then just return the first one we get.  As
        # the version are sorted by date, this should generally be the latest
        # plugin anyway.
        vobj = plugin.versions[0]
    else:
        # Otherwise we will need to parse though each version until we find
        # a name match, then return that.
        for vitem in plugin.versions:
            if vitem.version == version:
                vobj = vitem
    if vobj is None:
        return jsonify({'error': 'Version %s does not exist' % version})
    pdata = plugin.json()
    pdata['versions'] = vobj.json()
    return jsonify(pdata)


@app.route('/<repo>/plugin/<name>/<version>/download')
def plugin_download(repo, name, version, s):
    # Performs the same lookup as the version query does (and all of the same
    # hackery) however just simply replies with a redirect to the file's URL.
    # This makes it possible to very easily download specific versions of
    # a plugin using the API to handle the dirty work for you.
    plugin = s.query(db.Plugin).filter_by(name=name, repo=repo).first()

    if plugin is None:
        return jsonify({'error': 'Plugin %s does not exist' % name})

    vobj = None
    if version == 'latest':
        vobj = plugin.versions[0]
    else:
        for vitem in plugin.versions:
            if vitem.version == version:
                vobj = vitem
    if vobj is None:
        return jsonify({'error': 'Version %s does not exist' % version})
    redirect(vobj.download)


@app.route('/categories')
def categories(s):
    # Get all of the categories in the system and return a list of them
    categories = s.query(db.Category).all()
    cdata = [c.name for c in categories]
    return jsonify(cdata)


@app.route('/<repo>/category/<category>')
def category_plugin_list(repo, category, s, convert=True):
    # This function will return a list of all of plugins 
    
    # First we need to initialize everything
    start = request.query.start or 0
    size = request.query.size or -1
    fstring = request.query.fields or 'name,plugname,description'
    
    # For the data that were were accepting input, lets go
    # ahead and sanatize the input of any potential evil ;)
    fields = ['plugin.%s' % f for f in bleach.clean(fstring).split(',')]
    repo = bleach.clean(repo)
    start = int(bleach.clean(start))
    size = int(bleach.clean(size))

    # This is the query that we will be sending on to raw_sql
    # for processing.
    query = '''
        SELECT %s 
          FROM plugin, category, catagory_associations as ca
         WHERE plugin.repo = '%s'
           AND category.name = '%s'
           AND ca.plugin_id = plugin.id
           AND ca.category_id = category.id
         ORDER BY name
    ''' % (','.join(fields), repo, category)

    if size > 0:
        query += ' LIMIT %d, %d' % (start, size)

    # And now we hand off all of the fun bits to raw_sql ;)
    data = raw_sql(query, request, s, fields, start, size)
    if convert:
        return jsonify(data)
    else:
        return data


@app.route('/authors')
def author_list(s):
    authors = s.query(db.Author).all()
    adata = [a.name for a in authors]
    return jsonify(adata)


@app.route('/author/<name>')
def author_plugins(name, s):
    author = s.query(db.Author).filter_by(name=name).first()
    if author is None:
        return jsonify({'error': 'Author %s does not exist' % name})
    pdata = [p.json('name', 'plugname', 'description', 'repo') for p in author.plugins]
    return jsonify(pdata)


@app.route('/search/<obj>/<field>/<oper>/<value>')
def search(obj, field, oper, value, s, convert=True):
    # First we need to initialize everything
    start = request.query.start or 0
    size = request.query.size or -1
    fstring = request.query.fields or 'name,plugname,description'
    
    # For the data that were were accepting input, lets go
    # ahead and sanatize the input of any potential evil ;)
    fields = ['plugin.%s' % f for f in bleach.clean(fstring).split(',')]
    obj = bleach.clean(obj)
    field = bleach.clean(field)
    value = bleach.clean(value)
    start = int(bleach.clean(start))
    size = int(bleach.clean(size))

    # As this is repository indepentent, we need to make sure that the
    # repo field is listed so we know which repo a plugin is in.  We will also
    # make sure to remove the plugin.name field as thats already statically in
    # the query.
    if 'plugin.name' in fields:
        del fields[fields.index('plugin.name')]
    fields.append('plugin.repo')

    # Next we are going to have to determine what kind of filter we are going
    # to need and build it.
    if oper in ['=', '>', '>=', '<', '<=']:
        search = 'UPPER(%s) %s \'%s\'' % ('%s.%s' % (obj, field), oper, value.upper())
    elif oper in ['in', 'like']:
        search = 'UPPER(%s) LIKE \'%%%s%%\'' % ('%s.%s' % (obj, field), value.upper())
    else:
        return jsonify({'ERROR': 'Invalid Search Terms'})

    # Next we need to make sure that we can even perform this search.  We need
    # to make sure that the only tables that we will search from is version and
    # plugin.
    if obj not in ['plugin', 'version']:
        return jsonify({'ERROR': 'Invalid Object Name'})

    # This is the query that we will be sending on to raw_sql
    # for processing.
    query = '''
        SELECT DISTINCT plugin.name, %s 
          FROM plugin, version
         WHERE version.plugin_id = plugin.id
           AND %s
         ORDER BY plugin.name
    ''' % (','.join(fields), search)

    if size > 0:
        query += ' LIMIT %d, %d' % (start, size)

    # And now we add the plugin.name back into fields ;)
    fields.insert(0, 'plugin.name')
    
    # And now we hand off all of the fun bits to raw_sql ;)
    data = raw_sql(query, request, s, fields, start, size)
    if convert:
        return jsonify(data)
    else:
        return data
