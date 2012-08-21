from bottle import Bottle, request, response, template, redirect
from sqlalchemy import desc, and_, or_
from bottle.ext import sqlalchemy
from bukget.config import config
import bukget.db as db
import datetime
import time
import json

app = Bottle()
app.install(sqlalchemy.Plugin(db.disk, db.Base.metadata, keyword='s'))

def jsonify(dataset):
    return json.dumps(dataset)


def getdict(plugin, version_name=None):
    out = {
        'name': plugin.name,
        'bukkitdev_link': 'http://dev.bukkit.org/server-mods/%s/' % plugin.plugname,
        'categories': [c.name for c in plugin.categories],
        'desc': plugin.description,
        'plugin_name': plugin.plugname,
        'status': plugin.stage,
        'versions': []
    }
    if version_name == 'latest':
        version_name = versions[0].name

    for version in plugin.versions:
        if version_name is not None and version.name == version_name or\
           not version_name:
            out['versions'].append({
                    'date': int(time.mktime(version.date.timetuple())),
                    'dl_link': version.link,
                    'filename': version.filename,
                    'game_builds': version.game_versions,
                    'hard_dependencies': version.hard_dependencies,
                    'soft_dependencies': version.soft_dependencies,
                    'status': version.status,
                    'type': version.type,
                })
    return out



@app.hook('before_request')
def set_json_header():
    response.set_header('Content-Type', 'application/json')


@app.route('/')
def metadata(s):
    meta = s.query(db.Meta).order_by(desc(db.Meta.id)).first()
    return jsonify(meta.json())


@app.route('/plugins')
def plugin_list(s):
    plugins = s.query(db.Plugin).filter_by(repo='bukkit').all()
    plist = [a.name for a in plugins]
    return jsonify(plist)


@app.route('/plugin/<name>')
def plugin_details(name, s):
    plugin = s.query(db.Plugin).filter_by(name=name, repo='bukkit').first()
    return jsonify(getdict(plugin))


@app.route('/plugin/<name>/<version>')
def plugin_version(name, version, s):
    plugin = s.query(db.Plugin).filter_by(name=name, repo='bukkit').first()
    return jsonify(getdict(plugin, version))


@app.route('/plugin/<name>/<version>/download')
def plugin_download(name, version, s):
    plugin = s.query(db.Plugin).filter_by(name=name, repo='bukkit').first()
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


@app.route('/category/<category>')
def category_plugin_list(category, s):
    category = category.replace('_', ' ')
    category = s.query(db.Category).filter_by(name=category).first()
    pdata = []
    for plugin in category.plugins:
        if plugin.repo == 'bukkit':
            pdata.append(plugin.name)
    return jsonify(pdata)


@app.route('/authors')
def author_list(s):
    authors = s.query(db.Author).all()
    adata = [a.name for a in authors]
    return jsonify(adata)


@app.route('/author/<name>')
def author_plugins(name, s):
    author = s.query(db.Author).filter_by(name=name).first()
    pdata = [p.name for p in author.plugins]
    return jsonify(pdata)


@app.route('/search/<field>/<oper>/<value>')
@app.route('/search/<obj>/<field>/<oper>/<value>')
def search(field, oper, value, s, obj='plugin'):
    if oper in ['=', '>', '>=', '<', '<=']:
        search = '%s %s \'%s\'' % ('%s.%s' % (obj, field), oper, value)
    elif oper in ['in', 'like']:
        search = 'UPPER(%s) LIKE \'%%%s%%\'' % ('%s.%s' % (obj, field), value.upper())
    else:
        return jsonify({'ERROR': 'Invalid Search Terms'})
    if obj == 'plugin':
        items = s.query(db.Plugin).filter(search).all()
        pdata = [p.name for p in items]
    elif obj == 'version':
        items = s.query(db.Version).filter(search).all()
        pdata = [p.plugin.name for p in items]
    else:
        return jsonify({'ERROR': 'Invalid Object Name'})
    return jsonify(pdata)
