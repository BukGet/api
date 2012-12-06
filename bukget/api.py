import pymongo
import json
from bottle import Bottle, run, redirect, response, request

connection = Connection('localhost', 27017)
db = connection.bukget
app = Bottle()


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


@app.get('/plugin/<server>/<slug>')
def plugin(server, slug):
    '''
    '''
    