from bottle import template, request, response, redirect, Bottle
import config
import json
import dbo

cache = None
app = Bottle()

def update_cache():
    global cache
    try:
        cache = {
            'meta': dbo.meta_cache(),
            'plugins': dbo.plugin_cache(),
            'categories': dbo.category_cache(),
            }
    except:
        dbo.update()
        update_cache()

def seval(item, name, action, value):
    if name in item:
        try:
            if action == '=':
                if value == item[name]:
                    return True
            if action == '<':
                if int(value) < int(item[name]):
                    return True
            if action == '<=':
                if int(value) <= int(item[name]):
                    return True
            if action == '>':
                if int(value) > int(item[name]):
                    return True
            if action == '>=':
                if int(value) >= int(item[name]):
                    return True
            if action == 'in':
                if value in item[name]:
                    return True
            if action == 'like':
                if len(re.findall(value, item[name])) > 0:
                    return True
        except:
            return False
    return False

@app.route('/')
def metadata():
    response.headers['Content-Type'] = 'application/json'
    return json.dumps(cache['meta'].dict(), sort_keys=True, indent=4)

@app.route('/update')
@app.route('/update/:load_type')
def update(load_type='speedy'):
    response.headers['Content-Type'] = 'application/json'
    if request['REMOTE_ADDR'] == '127.0.0.1':
        conf = config.Configuration()
        if load_type == 'full':
            speedy = False
        else:
            speedy = True
        resp = dbo.update(speedy)
        update_cache()
        return json.dumps(resp, sort_keys=True, indent=4)

@app.route('/plugins')
def plugin_list():
    response.headers['Content-Type'] = 'application/json'
    items = []
    for item in cache['plugins']:
        items.append(item.name)
    return json.dumps(sorted(items), sort_keys=True, indent=4)

@app.route('/plugin/:name')
def plugin_details(name):
    response.headers['Content-Type'] = 'application/json'
    for item in cache['plugins']:
        if item.name == name:
            return json.dumps(item.dict(), sort_keys=True, indent=4)
    return ''

@app.route('/plugin/:name/:version')
def latest_plugins(name, version):
    response.headers['Content-Type'] = 'application/json'
    for item in cache['plugins']:
        if item.name == name:
            return json.dumps(item.dict(version=version.replace('_', ' ')), 
                              sort_keys=True, indent=4)
    return ''

@app.route('/plugin/:name/:version/download')
def latest_plugin_download(name, version):
    response.headers['Content-Type'] = 'application/json'
    for item in cache['plugins']:
        if item.name == name:
            if version == 'latest':
                redirect(item.versions[0].link)
            else:
                for ver in item.versions:
                    if ver.name.lower() == version.replace('_', ' ').lower():
                        redirect(ver.link)
    return ''

@app.route('/categories')
def category_list():
    response.headers['Content-Type'] = 'application/json'
    return json.dumps(cache['categories'], sort_keys=True, indent=4)

@app.route('/category/:name')
def category_plugins(name):
    response.headers['Content-Type'] = 'application/json'
    cat_name = name.replace('_', ' ')
    items = []
    for item in cache['plugins']:
        if cat_name in item.get('categories'):
            items.append(item.name)
    return json.dumps(sorted(items), sort_keys=True, indent=4)

@app.route('/search', method='POST')
@app.route('/search/:field/:action/:value')
def search(field=None, action=None, value=None):
    items = []
    response.headers['Content-Type'] = 'application/json'
    if request.method == 'POST':
        field = str(request.forms.get('fieldname'))
        action = str(request.forms.get('action'))
        value = str(request.forms.get('value'))    
    if field_name[:2] == 'v_':
        in_versions = True
        field_name = field_name[2:]
    else:
        in_versions = False
    for item in cache['plugins']:
        dset = item.dict()
        version = {}
        match = False
        if in_versions:
            for version in item['versions']:
                match = seval(version, field_name, action, value)
        else:
            match = seval(data, field_name, action, value)
        if match:
            items.append(data['name'])
    return json.dumps(items, sort_keys=True, indent=4)

@app.route('/json')
def json_dump():
    response.headers['Content-Type'] = 'application/json'
    items = []
    for item in cache['plugins']:
        items.append(item.dict())
    return json.dumps(items, sort_keys=True, indent=4)

@app.route('/json/latest')
def json_dump():
    response.headers['Content-Type'] = 'application/json'
    items = []
    for item in cache['plugins']:
        items.append(item.dict(latest=True))
    return json.dumps(items, sort_keys=True, indent=4)