import pymongo
from bson.code import Code

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

connection = pymongo.MongoClient('localhost', 27017)
db = connection.bukget

def plugins(filters=[], finc=[], fexc=[], size=-1, start=-1, sort='slug',
            sub=False, single=False):
    '''
    '''
    fields = {'_id': 0}
    f = {}
    for item in fexc: fields[item] = 0
    for item in finc: fields[item] = 1
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
        return db.plugins.find_one(f, fields)
    else:
        data = list(db.plugins.find(f, fields).sort(sort))
        if size > 0 and start >= 0:
            data = data[start:start+size]
        return data


def categories():
    '''
    '''
    data = []
    for item in db.plugins.map_reduce(cmap, reduceall, 'clist').find().sort('_id'):
        data.append({'name': item['_id'], 'count': item['value']})
    return data


def authors():
    '''
    '''
    data = []
    for item in db.plugins.map_reduce(amap, reduceall, 'alist').find().sort('_id'):
        data.append({'name': item['_id'], 'count': item['value']})
    return data

