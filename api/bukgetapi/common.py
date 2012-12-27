import pymongo
import json
import re
from bson.code import Code
from bson.objectid import ObjectId
from ConfigParser import ConfigParser

config = ConfigParser()
config.read('/etc/bukget/api.conf')

connection = pymongo.MongoClient(config.get('Settings', 'database_host'), 
                                 config.getint('Settings', 'database_port'))
db = connection.bukget

amap = Code('''
function () {
    this.authors.forEach(function(z) {
        emit(z, 1);
    });
}
''')

cmap = Code('''
function () {
    this.categories.forEach(function(z) {
        emit(z, 1);
    });
}

''')

reduceall = Code('''
function (key, values) {
    var total = 0;
    for (var i = 0; i < values.length; i++) {
        total += values[i];
    }
    return total;
}
''')


def ignore_exception(IgnoreException=Exception,DefaultVal=None):
    ''' Decorator for ignoring exception from a function
    e.g.   @ignore_exception(DivideByZero)
    e.g.2. ignore_exception(DivideByZero)(Divide)(2/0)
    From: sharjeel
    Source: stackoverflow.com
    '''
    def dec(function):
        def _dec(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except IgnoreException:
                return DefaultVal
        return _dec
    return dec
sint = ignore_exception(ValueError)(int)


def jsonify(data):
    '''
    '''
    return json.dumps(data)


def fieldgen(fields):
    '''
    Generates the field listing based on the include and exclude lists.
    '''
    f = {'_id': 0}
    for item in fields:
        if str(item) is not '':
            if item[0] == '-':
                f[item[1:]] = 0
            else:
                f[item] = 1
    return f


def list_geninfo(size=1):
    '''
    This function allows for the retreival of the last X number of generations
    based on the value of the size variable.
    '''
    if size is None:
        size = 1
    infos = db.geninfo.find().sort('_id', -1).limit(size)
    data = []
    for item in infos:
        item['id'] = str(item['_id'])
        del(item['_id'])
        data.append(item)
    return data


def get_geninfo(idnum):
    '''
    Returns a specific generation IDs information.
    '''
    item = db.geninfo.find_one({'_id': ObjectId(idnum)})
    if item is not None:
        item['id'] = str(item['_id'])
        del(item['_id'])
    return item


def list_plugins(server, fields, sort):
    '''
    This function returns a list of plugins with the fields specified.  The 
    list can be narrowed down to specific server binary compatability by
    specifying the server as something other than None.
    '''
    filters = {}
    if server is not None:
        filters['server'] = server
    return list(db.plugins.find(filters, fieldgen(fields)).sort(sort))


def list_author_plugins(server, author, fields, sort):
    '''
    Returns the plugin list for a given author.  Furthermore by setting the
    server to something other than None, it's possible to specify a specific
    server binary compatability.
    '''
    filters = {'authors': author}
    if server is not None:
        filters['server'] = server
    return list(db.plugins.find(filters, fieldgen(fields)).sort(sort))


def list_category_plugins(server, category, fields, sort):
    '''
    Returns the plugin list for a given author.  Furthermore by setting the
    server to something other than None, it's possible to specify a specific
    server binary compatability.
    '''
    filters = {'categories': category}
    if server is not None:
        filters['server'] = server
    return list(db.plugins.find(filters, fieldgen(fields)).sort(sort))


def list_authors():
    '''
    Returns a list of plugin authors and the number of plugins each one has
    created/worked on.
    '''
    data = []
    for item in db.plugins.map_reduce(amap, reduceall, 'authors').find().sort('_id'):
        data.append({'name': item['_id'], 'count': item['value']})
    return data


def list_categories():
    '''
    Returns a list of plugin categories and the count of plugins that fall under
    each category.
    '''
    data = []
    for item in db.plugins.map_reduce(cmap, reduceall, 'categories').find().sort('_id'):
        data.append({'name': item['_id'], 'count': item['value']})
    return data


def plugin_details(server, plugin, version, fields):
    '''
    Returns the plugin details for a given plugin.  Optionally will also
    return a specific version of the plugin in the versions list if something
    other than None is specified in the version variable.
    '''
    filters = {'slug': plugin, 'server': server}
    p = db.plugins.find_one(filters, fieldgen(fields))
    if version is not None:
        if version.lower() == 'latest':
            p['versions'] = [p['versions'][0]]
        else:
            p['versions'] = [v for v in p['versions'] if v['version'] == version]
    return p


def plugin_search(filters, fields, sort, sub=False):
    '''
    A generalized sort function for the database.  Returns a list of plugins
    with the fields specified in the incusion and exclusion variables.
    '''
    f = {}
    for item in filters:
        if item['action'] == '=': f[item['field']] = item['value']
        if item['action'] == '!=': f[item['field']] = {'$ne': item['value']}
        if item['action'] == '<': f[item['field']] = {'$lt': item['value']}
        if item['action'] == '<=': f[item['field']] = {'$lte': item['value']}
        if item['action'] == '>': f[item['field']] = {'$gt': item['value']}
        if item['action'] == '>=': f[item['field']] = {'$gte': item['value']}
        if item['action'] == 'like': f[item['field']] = re.compile(r'%s' % item['value'])
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
    if sub: return f
    return list(db.plugins.find(f, fieldgen(fields)).sort(sort))
