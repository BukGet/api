import pymongo
import json
from bottle import Bottle, run, redirect, response, request

connection = Connection('localhost', 27017)
db = connection.bukget
plugins = db.plugins
geninfo = dp.geninfo
app = Bottle()


def getplugins(filters=[], finc=[], fexc=[], sub=False, single=False):
    '''
    '''
    fields = {'_id': 0}
    f = {}
    for item in finc: fields[item] = 1
    for item in fexc: fields[item] = 0
    for item in filters:
        if item['action'] == '=': f[item['field']] = item['value']
        if item['action'] == '!=': f[item['field']] = {'$ne': item['value']}
        if item['action'] == '<': f[item['field']] = {'$lt': item['value']}
        if item['action'] == '<=': f[item['field']] = {'$lte': item['value']}
        if item['action'] == '>': f[item['field']] = {'$gt': item['value']}
        if item['action'] == '>=': f[item['field']] = {'$gte': item['value']}
        if item['action'] == 'in': 
            if isinstance(item['value'], list):
                f[item['field']] = {'$in': item['value']}
        if item['action'] == 'not in':
            if isinstance(item['value'], list):
                f[item['field']] = {'$nin': item['value']}
        if item['action'] == 'all':
            if isinstance(item['value'], list):
                f[item['field']] = {'$all': item['value']}
        if item['action'] == 'and':
            if isinstance(item['value'], list) and item['field'] == '':
                f['$and'] = get(item['value'], sub=True)
        if item['action'] == 'or':
            if isinstance(item['value'], list) and item['field'] == '':
                f['$or'] = get(item['value'], sub=True)
        if item['action'] == 'nor':
            if isinstance(item['value'], list) and item['field'] == '':
                f['$nor'] = get(item['value'], sub=True)
        if item['action'] == 'not':
            if isinstance(item['value'], list) and item['field'] == '':
                f['$not'] = get(item['value'], sub=True)
    if sub:
        return f
    elif single:
        return plugins.find_one(filters, fields)
    else:
        return plugins.find(filters, fields)



@app.post('/plugin')
def update_plugin():
    '''
    '''
    plugin = json.loads(request.forms.get('data'))
    try:
        db.plugins.update({'server': plugin['server'], 'slug': plugin['slug']}, 
                          {'$set': plugin})
    except:
        db.plugins.insert(plugin)


@app.post('/geninfo')
def new_gen():
    '''
    '''
    geninfo = json.loads(request.forms.get('data'))
    db.geninfo.insert(geninfo)


@app.get('/plugins')
@app.get('/plugins/')
@app.get('/plugins/<server>')
def plugin_list(server=None):
    '''
    '''



@app.get('/plugins/<server>/<slug>')
@app.get('/plugins/<server>/<slug>/')
@app.get('/plugins/<server>/<slug>/<version>')
def plugin_details(server, slug, version=None):
    '''
    '''


@app.get('/plugins/<server>/<slug>/<version>/download')
def plugin_download(server, slug, version):
    '''
    '''


@app.get('/authors')
@app.get('/authors/')
def author_list():
    '''
    '''


@app.get('/authors/<name>')
def author_plugins(name):
    '''
    '''


@app.get('/categories')
@app.get('/categories/')
def category_list():
    '''
    '''


@app.get('/categories/<name>')
@app.get('/categories/<server>/<name>')
def category_plugins(name, server=None):
    '''
    '''


@app.post('/search')
@app.get('/search/<field>/<action>/<value>')
def search(field=None, action=None, value=None):
    '''
    '''