from bottle import Bottle, request, response, template, redirect
from sqlalchemy import desc, and_, or_
from bottle.ext import sqlalchemy
from bukget.config import config
import bukget.db as db
import json

app = Bottle()
app.install(sqlalchemy.Plugin(db.disk, db.Base.metadata, keyword='s'))

def jsonify(dataset):
    return json.dumps(dataset)


@app.hook('before_request')
def set_json_header():
    response.set_header('Content-Type', 'application/json')


@app.route('/')
def metadata(s):
    meta = s.query(db.Meta).order_by(desc(db.Meta.id)).first()
    return jsonify(meta.json())


@app.route('/<repo>/plugins')
def plugin_list(repo, s):
    plugins = s.query(db.Plugin).filter_by(repo=repo).all()
    plist = [a.json('name', 'plugname', 'description') for a in plugins]
    return jsonify(plist)


@app.route('/<repo>/plugin/<name>')
def plugin_details(repo, name, s):
    plugin = s.query(db.Plugin).filter_by(name=name, repo=repo).first()
    pdata = plugin.json()
    return jsonify(pdata)


@app.route('/<repo>/plugin/<name>/<version>')
def plugin_version(repo, name, version, s):
    plugin = s.query(db.Plugin).filter_by(name=name, repo=repo).first()
    if version == 'latest':
        vobj = plugin.versions[0]
    else:
        for vitem in plugin.versions:
            if vitem.version == version:
                vobj = vitem
    pdata = plugin.json()
    pdata['versions'] = vobj.json()
    return jsonify(pdata)


@app.route('/<repo>/plugin/<name>/<version>/download')
def plugin_download(repo, name, version, s):
    plugin = s.query(db.Plugin).filter_by(name=name, repo=repo).first()
    if version == 'latest':
        vobj = plugin.versions[0]
    else:
        for vitem in plugin.versions:
            if vitem.version == version:
                vobj = vitem
    redirect(vobj.download)


@app.route('/categories')
def categories(s):
    categories = s.query(db.Category).all()
    cdata = [c.name for c in categories]
    return jsonify(cdata)


@app.route('/<repo>/category/<category>')
def category_plugin_list(repo, category, s):
    category = category.replace('_', ' ')
    category = s.query(db.Category).filter_by(name=category).first()
    pdata = []
    for plugin in category.plugins:
        if plugin.repo == repo:
            pdata.append(plugin.json('name', 'plugname', 'description'))
    return jsonify(pdata)


@app.route('/authors')
def author_list(s):
    authors = s.query(db.Author).all()
    adata = [a.name for a in authors]
    return jsonify(adata)


@app.route('/author/<name>')
def author_plugins(name, s):
    author = s.query(db.Author).filter_by(name=name).first()
    pdata = [p.json('name', 'plugname', 'description', 'repo') for p in author.plugins]
    return jsonify(pdata)


@app.route('/search/<obj>/<field>/<oper>/<value>')
def search(obj, field, oper, value, s):
    if oper in ['=', '>', '>=', '<', '<=']:
        search = '%s %s \'%s\'' % ('%s.%s' % (obj, field), oper, value)
    elif oper in ['in', 'like']:
        search = 'UPPER(%s) LIKE \'%%%s%%\'' % ('%s.%s' % (obj, field), value.upper())
    else:
        return jsonify({'ERROR': 'Invalid Search Terms'})
    if obj == 'plugin':
        items = s.query(db.Plugin).filter(search).all()
        pdata = [p.json('name', 'plugname', 'description', 'repo') for p in items]
    elif obj == 'version':
        items = s.query(db.Version).filter(search).all()
        pdata = [p.plugin.json('name', 'plugname', 'description', 'repo') for p in items]
    else:
        return jsonify({'ERROR': 'Invalid Object Name'})
    return jsonify(pdata)
