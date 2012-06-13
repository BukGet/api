from bottle import Bottle, request, response, template, redirect
from bukget.config import config
import bukget.db as db
import bukget.svc as svc

app = Bottle()

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
    return plist


@app.route('/<repo>/plugin/<name>')
def plugin_details(repo, name):
    s = db.Reactor()
    plugin = s.query(db.Plugin).filter_by(name=name, repo=repo).first()
    pdata = plugin.json()
    s.close()
    return pdata


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
    return pdata


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
    return cdata


@app.route('/<repo>/category/<category>')
def category_plugin_list(repo, category):
    s = db.Reactor()
    