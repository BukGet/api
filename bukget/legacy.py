from bottle import Bottle, request, response, template, redirect, error
from sqlalchemy import desc, and_, or_
from bottle.ext import sqlalchemy
from bukget.config import config
import bukget.db as db
import bukget.api as api
import datetime
import time
import json

app = Bottle()
app.install(sqlalchemy.Plugin(db.disk, db.Base.metadata, keyword='s'))

def jsonify(dataset):
    return json.dumps(dataset)


def getdict(plugin, version_name=None):
    if plugin is None:
        return {'error': 'Plugin %s does not exist' % name}

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
        version_name = plugin.versions[0].version

    for version in plugin.versions:
        if version_name is not None and version.name == version_name or\
           not version_name:
            out['versions'].append({
                    'name': version.version,
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



@error(404)
@error(500)
def error404(error):
    return jsonify({'ERROR': 'Bad Request'})


@app.route('/')
def metadata(s):
    meta = s.query(db.Meta).order_by(desc(db.Meta.id)).first()
    return jsonify(meta.json())


@app.route('/plugins')
def plugin_list(s):
    plugins = api.plugin_list('bukkit', s, convert=False)
    return jsonify([a['name'] for a in plugins])


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
    categories = s.query(db.Category).all()
    return jsonify([c.name for c in categories])


@app.route('/category/<category>')
def category_plugin_list(category, s):
    plugins = api.category_plugin_list('bukkit', category, s, convert=False)
    return jsonify([p['name'] for p in plugins])


@app.route('/authors')
def author_list(s):
    authors = s.query(db.Author).all()
    return jsonify([a.name for a in authors])


@app.route('/author/<name>')
def author_plugins(name, s):
    author = s.query(db.Author).filter_by(name=name).first()
    if author is None:
        return jsonify({'error': 'Author %s does not exist' % name})
    pdata = [p.name for p in author.plugins]
    return jsonify(pdata)


@app.route('/search/<field>/<oper>/<value>')
@app.route('/search/<obj>/<field>/<oper>/<value>')
def search(field, oper, value, s, obj='plugin'):
    plugins = api.search(obj, field, oper, value, s, convert=False)
    return jsonify([p['name'] for p in plugins])
