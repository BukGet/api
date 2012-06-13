from bottle import Bottle, request, response, template, redirect
from bukget.config import config
import bukget.db as db
import bukget.svc as svc
import json

app = Bottle()


def jsonify(dataset):
    return json.dumps(dataset)


@app.hook('before_request')
def set_json_header():
    response.set_header('Content-Type', 'application/json')


@app.route('/')
def metadata():
    s = db.Reactor()
    repos = s.query(db.Repo).all()
    meta = []
    for repo in repos:
        meta.append(s.query(db.Meta).filter_by(repo_id=repo.id)\
                                    .order_by(db.desc(db.Meta.generation))\
                                    .first().json())
    s.close()
    return meta


@app.route('/<repo>/plugins')
def plugin_list(repo):
    s = db.Reactor()
    plugins = s.query(db.Plugin).filter_by(repo=repo).all()
    plist = [a.json('name', 'plugname', 'description') for a in plugins]
    s.close()
    return jsonify(plist)


@app.route('/<repo>/plugin/<name>')
def plugin_details(repo, name):
    s = db.Reactor()
    plugin = s.query(db.Plugin).filter_by(name=name, repo=repo).first()
    pdata = plugin.json()
    s.close()
    return jsonify(pdata)


@app.route('/<repo>/plugin/<name>/<version>')
def plugin_version(repo, name, version):
    s = db.Reactor()
    plugin = s.query(db.Plugin).filter_by(name=name, repo=repo).first()
    if version == 'latest':
        vobj = plugin.versions[0]
    else:
        for vitem in plugin.versions:
            if vitem.version == version:
                vobj = vitem
    pdata = plugin.json()
    pdata['versions'] = vobj.json()
    s.close()
    return jsonify(pdata)


@app.route('/<repo>/plugin/<name>/<version>/download')
def plugin_download(repo, name, version):
    s = db.Reactor()
    plugin = s.query(db.Plugin).filter_by(name=name, repo=repo).first()
    if version == 'latest':
        vobj = plugin.versions[0]
    else:
        for vitem in plugin.versions:
            if vitem.version == version:
                vobj = vitem
    redirect(vobj.download)


@app.route('/categories')
def categories(repo):
    s = db.Reactor()
    categories = s.query(db.Category).all()
    cdata = [c.json('name') for c in categories]
    s.close()
    return jsonify(cdata)


@app.route('/<repo>/category/<category>')
def category_plugin_list(repo, category):
    s = db.Reactor()
    category = category.replace('_', ' ')
    category = s.query(db.Category).filter_by(name=name).first()
    pdata = []
    for plugin in category.plugins:
        if plugin.repo == repo:
            pdata.append(plugin.json('name', 'plugname', 'description'))
    s.close()
    return jsonify(pdata)


@app.route('/authors')
def author_list():
    s = db.Reactor()
    authors = s.query(db.Author).all()
    adata = [a.json('name') for a in authors]
    s.close()
    return jsonify(adata)


@app.route('/author/<name>')
def author_plugins(name):
    s = db.Reactor()
    author = s.query(db.Author).filter_by(name=name).first()
    pdata = [p.json('name', 'plugname', 'description', 'repo') for p in author.plugins]
    s.close()
    return jsonify(pdata)