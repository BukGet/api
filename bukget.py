#!/usr/bin/env python
import os
from ConfigParser import ConfigParser

#### CONFIGURATION AND PRE-PROCESSING
# The script has to run from the location on disk that it lives.
os.chdir(os.path.dirname(__file__))

config = ConfigParser()

def reload_config():
    config.read('bukget.ini')

reload_config()

# Activate the virtualenv
if config.getboolean('Settings', 'virtual_env'):
    activate_this = '../bin/activate_this.py'
    execfile(activate_this, dict(__file__=activate_this))


from sqlalchemy import (Table, Column, Integer, String, DateTime, Date, 
                        ForeignKey, Text, Boolean, MetaData, 
                        and_, desc)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, joinedload, subqueryload
from BeautifulSoup import BeautifulSoup as bsoup
from urllib import urlopen
from zipfile import ZipFile
from StringIO import StringIO
from bottle import (run, debug, template, request, response, abort, redirect, 
                    static_file, Bottle)
from ConfigParser import ConfigParser
import datetime
import yaml
import json
import time
import re

app = Bottle()
jdict = []
meta = {}

sql_string = config.get('Settings', 'db_string')
engine = create_engine(sql_string)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Plugin(Base):
    __tablename__ = 'plugin'
    id = Column(Integer(8), primary_key=True)
    name = Column(String(128), unique=True)
    full_name = Column(String(128))
    categories = Column(Text)
    authors = Column(Text)
    status = Column(String(32))
    link = Column(Text)
    versions = relationship('Version', order_by='desc(Version.date)', 
                            backref='plugin')
    
    def __init__(self, name, authors, categories, link, status, fname):
        self.name = name
        self.link = link
        self.update(authors=authors, categories=categories, status=status,
                    fname=fname)
    
    def _list_parser(self, slist):
        if isinstance(slist, unicode) or isinstance(slist, str):
            data = slist.split(',')
        else:
            data = slist
        vals = []
        for item in data:
            vals.append(item.strip())
        return vals
    
    def update(self, authors=None, categories=None, status=None, fname=None):
        if authors is not None:
            self.authors = ', '.join(self._list_parser(authors))
        if categories is not None:
            self.categories = ', '.join(self._list_parser(categories))
        if status is not None:
            self.status = status
        if fname is not None:
            self.full_name = fname
    
    def get(self, item):
        if item == 'authors':
            return self._list_parser(self.authors)
        if item == 'categories':
            return self._list_parser(self.categories)
        return None
Plugin.metadata.create_all(engine)
    
class Version(Base):
    __tablename__ = 'version'
    id = Column(Integer(8), primary_key=True)
    name = Column(String(32))
    link = Column(Text)
    date = Column(DateTime)
    cb_versions = Column(Text)
    filename = Column(String(32))
    md5 = Column(String(32))
    hard_dependencies = Column(Text)
    soft_dependencies = Column(Text)
    plugin_id = Column(Integer(8), ForeignKey('plugin.id'))
    
    def __init__(self, name, date, link, cb_versions, filename, md5, 
                 soft_deps, hard_deps, plugin_id):
        self.name = name
        self.link = link
        self.date = date
        self.cb_versions = ', '.join(self._list_parser(cb_versions))
        self.filename = filename
        self.md5 = md5
        self.hard_dependencies = ', '.join(self._list_parser(hard_deps))
        self.soft_dependencies = ', '.join(self._list_parser(soft_deps))
        self.plugin_id = plugin_id
    
    def _list_parser(self, slist):
        if isinstance(slist, unicode) or isinstance(slist, str):
            data = slist.split(',')
        else:
            data = slist
        vals = []
        for item in data:
            if len(item) > 0:
                vals.append(item.strip())
        return vals
    
    def get(self, item):
        if item == 'cb_versions':
            return self._list_parser(self.cb_versions)
        if item == 'soft_dependencies':
            return self._list_parser(self.soft_dependencies)
        if item == 'hard_dependencies':
            return self._list_parser(self.hard_dependencies)
Version.metadata.create_all(engine)

class Meta(Base):
    __tablename__ = 'metadata'
    id = Column(Integer(8), primary_key=True)
    date = Column(DateTime)
    time = Column(Integer(8))
    start_time = None
    
    def __init__(self):
        self.start_time = datetime.datetime.now()
    
    def finish(self):
        self.date = datetime.datetime.now()
        self.time = (self.date - self.start_time).seconds
        
Meta.metadata.create_all(engine)

class History(Base):
    __tablename__ = 'history'
    id = Column(Integer(8), primary_key=True)
    meta_id = Column(Integer(8), ForeignKey('metadata.id'))
    plugin_name = Column(Text)
    version_name = Column(Text)
    meta = relationship('Meta', backref='history')
    
    def __init__(self, meta_id, plugin, version):
        self.meta_id = meta_id
        self.plugin_name = plugin
        self.version_name = version
History.metadata.create_all(engine)

def get(delay=2, host='http://dev.bukkit.org', debug=False, speedy=False):
    start = datetime.datetime.now()
    s = Session()
    
    # Here we instantiate and add the metadata row to the database.  We will
    # be using this for historical reasons and will need the id for the
    # history rows.
    meta = Meta()
    s.add(meta)
    s.commit()
    
    url = '%s/server-mods' % host
    plugins = []
    
    curl = url
    phase1 = True
    while phase1:
        count = 0
        if debug:
            print 'Opening %s' % curl
        page = bsoup(urlopen(curl))
        
        # First thing we need to pull all of the row items in the page that
        # contain the data that we are looking for.
        projects = page.findAll(attrs={'class': ['even row-joined-to-next',
                                                 'odd row-joined-to-next']})
        
        # Next, we parse through each row to get the desired data.
        for project in projects:
            # First we need to pull out the info from the fields in the row.
            proj_raw = project.findNext(attrs={'class': 'col-project'})\
                               .findNext('a')
            cat_raw = project.findNext(attrs={'class': 'category-list'})\
                             .findAll('li')
            user_raw = project.findAll(attrs={'class': 'user user-author'})
            status = project.findNext(attrs={'class': 'col-status'}).text
            link = '%s%s' % (host, proj_raw.get('href'))
            
            # Yes this is a bit of a hack.  However this should hopefully
            # escape the problem data.
            try:
                json.dumps(str(proj_raw.text).replace('\\', '\\\\'))
                fname = str(proj_raw.text).replace('\\', '\\\\')
            except:
                fname = ''
            
            # Now to parse through the category list and parse out the items.
            categories = []
            for cat in cat_raw:
                categories.append(cat.findNext('a').text)
            
            # Next to pull all of the authors of the plugin.
            authors = []
            for user in user_raw:
                authors.append(user.text)
            
            # Lastly we will parse out the plugin name.
            name = link.split('/')[-2]
            
            # Now to check to see if the plugin already exists in the
            # database.  if it does, then we will simply run the update
            # function to update any of the items to current.
            try:
                plugin = s.query(Plugin).filter_by(name=name).one()
            except:
                plugin = Plugin(name, authors, categories, link, status, 
                                fname)
                s.add(plugin)
            plugin.update(authors=authors, categories=categories, 
                          status=status, fname=fname)
            s.merge(plugin)
            s.commit()
            
            # Now we need to parse through all of the versions on the first
            # page of the files section.  We will do this because it decreases
            # the number of pages that we will need to parse.
            time.sleep(delay)
            purl = '%sfiles' % (link)
            if debug:
                print 'Opening %s' % purl
            ppage = bsoup(urlopen(purl))
            try:
                rows = ppage.findChild('tbody').findAll('tr')
            except:
                continue
            
            for row in rows:
                
                # Yay row parsing, yay!
                filelink = row.findNext(attrs={'class': 'col-file'})\
                              .findNext('a')
                rtype = row.findNext(attrs={'class': 'col-type'})\
                           .findNext('span').text
                fstatus = row.findNext(attrs={'class': 'col-status'})\
                             .findNext('span').text
                sdate = row.findNext(attrs={'class': 'col-date'})\
                           .findNext('span').get('data-epoch')
                vlist_raw = row.findNext(attrs={'class': 'col-game-version'})\
                           .findAll('li')
                fname = row.findNext(attrs={'class': 'col-filename'}).text
                md5sum = row.findNext(attrs={'class': 'col-md5'}).text
                
                # Now to break down the filelink variable to version name &
                # the link to the page that has the slug to the file.
                version_name = filelink.text
                version_link = '%s%s' % (host, filelink.get('href'))
                
                # Now to generate a proper datetime object based on this epoch
                version_date = datetime.datetime.fromtimestamp(float(sdate))
                
                # and now we parse out the CB Build numbers that this version
                # will work with.
                vlist = []
                for item in vlist_raw:
                    dset = item.text.split(' ')
                    if len(dset) > 1:
                        vlist.append(dset[1])
                
                # If the file isnt a Zipfile or a Jar file, then we can't
                # parse it, so lets just skip it.
                if len(fname.split('.')) > 1:
                    if fname.split('.')[-1].lower() not in ['zip','jar']:
                        continue
                
                try:
                    version = s.query(Version).filter_by(md5=md5sum).one()
                except:
                    count += 1
                    time.sleep(delay)
                    if debug:
                        print 'Opening %s' % version_link
                    
                    # Now we parse out the real file location
                    dlpage = bsoup(urlopen(version_link))
                    dl_link = dlpage.findChild(attrs={
                                'class': 'user-action user-action-download'})\
                                .findNext('a').get('href')
                    soft_deps = []
                    hard_deps = []
                    
                    # Here we will try to figure out the hard and soft
                    # dependencies.  This is in a try block as I can only
                    # assume that it will fail from time to time. and I would
                    # rather have a empty dependency set than the whole script
                    # fail out.
                    try:
                        dl_data = StringIO()
                        dl_data.write(urlopen(dl_link).read())
                        jar = ZipFile(dl_data)
                        if 'plugin.yml' in jar.namelist():
                            plugin_yaml = yaml.load(jar.read('plugin.yml'))
                            if 'depend' in plugin_yaml:
                                if plugin_yaml['depend'] is not None:
                                    hard_deps = plugin_yaml['depend']
                            if 'softdepend' in plugin_yaml:
                                if plugin_yaml['softdepend'] is not None:
                                    soft_deps = plugin_yaml['softdepend']
                        if debug:
                            print 'Soft: %s / Hard: %s' % (soft_deps, hard_deps)
                        jar.close()
                        dl_data.close()
                    except:
                        pass
                        
                    # Now we add this shiney new version to the database and
                    # commit it up so we don't loose it.
                    version = Version(version_name, version_date,
                                      dl_link, vlist, fname, md5sum,
                                      soft_deps, hard_deps, plugin.id)
                    
                    # Next we create the history object so that we can track
                    # the changes...
                    history = History(meta.id, plugin.name, version_name)
                    
                    s.add(version)
                    s.add(history)
                    s.commit()
        next = page.findAll(attrs={'class': 'listing-pagination-pages-next'})
        if count == 0 and speedy:
            phase1 = False
        elif len(next) > 0:
            link = next[0].findNext('a')
            curl = '%s%s' % (host, link.get('href'))
            time.sleep(delay)
        else:
            phase1 = False
            
    # Lastly, we will update the meta object to get the time it took to run
    # the generation and then merge the update.
    meta.finish()
    s.merge(meta)
    s.commit()
    s.close()

def jdata_dump(debug=False):
    s = Session()
    plugins = s.query(Plugin).all()
    jdata = []
    for plugin in plugins:
        versions = []
        for version in plugin.versions:
            versions.append({
                'name': version.name,
                'dl_link': version.link,
                'date': int(time.mktime(version.date.timetuple())),
                'filename': version.filename,
                'md5': version.md5,
                'game_builds': version.get('cb_versions'),
                'soft_dependencies': version.get('soft_dependencies'),
                'hard_dependencies': version.get('hard_dependencies')
            })
        try:
            json.dumps(plugin.full_name)
            plugin_name = plugin.full_name
        except:
            plugin_name = None
        jdata.append({
            'name': plugin.name,
            'plugin_name': plugin_name,
            'bukkitdev_link': plugin.link,
            'status': plugin.status,
            'authors': plugin.get('authors'),
            'categories': plugin.get('categories'),
            'versions': versions
        })
    s.close()
    return json.dumps(jdata, sort_keys=True, indent=4)

def meta_dump(meta_id=None):
    s = Session()
    if meta_id == None:
        metadata = s.query(Meta).order_by(desc(Meta.id)).limit(1).one()
    else:
        try:
            metadata = s.query(Meta).filter_by(id=meta_id).one()
        except:
            s.close()
            return {'error': 'id doesnt exist'}
    meta = {
        'id': metadata.id,
        'date': int(time.mktime(metadata.date.timetuple())),
        'duration': metadata.time,
        'changes': []
    }
    for item in metadata.history:
        meta['changes'].append({
            'plugin': item.plugin_name,
            'version': item.version_name
        })
    s.close()
    return json.dumps(meta, sort_keys=True, indent=4)

def parent_load(host):
    try:
        meta = json.loads(urlopen('http://%s/api').read())
        jdict = json.loads(urlopen('http://%s/api/json').read())
    except:
        return False
    s = Session()
    
    # Loading all the data from the API metadata into the database...
    meta_obj = Meta()
    meta_obj.id = meta['id']
    meta_obj.date = datetime.datetime.fromtimestamp(meta['date'])
    meta_obj.time = meta['duration']
    s.add(meta_obj)
    for item in meta['changes']:
        s.add(History(meta['id'], item['plugin'], item['version']))
    s.commit()
    
    # Now we will start cranking through all of the data in the plugin dump
    # and make the appropriate additions where necessary.  We will be parsing
    # everything, not just the changes.  This is to make sure that we realy do
    # have a full copy.
    

def update():
    global jdict
    global meta
    jdict = json.loads(jdata_dump())
    meta = json.loads(meta_dump())

def reload_config():
    config.read('bukget.ini')

@app.route('/blog')
@app.route('/repo/') 
def go_home():
    redirect('/')

@app.route('/')
@app.route('/index.html')
def home_page():
    data = open('content.md')
    content = data.read()
    data.close()
    return template('home_page', content=content, 
                    api=meta)

@app.route('/baskit')
def baskit_page():
    data = open('baskit.md')
    content = data.read()
    data.close()
    return template('home_page', content=content, 
                    api=meta)

@app.route('/static/:filename#.+#')
def route_static_files(filename):
    return static_file(filename, root='static')

@app.route('/favicon.ico')
def get_repo_file():
    return static_file('images/favicon.ico', 'static')

@app.route('/api')
def version_info():
    response.headers['Content-Type'] = 'application/json'
    return json.dumps(meta, sort_keys=True, indent=4)

@app.route('/api/history/:meta_raw')
def version_history(meta_raw):
    response.headers['Content-Type'] = 'application/json'
    try:
        meta_id = int(meta_raw)
    except:
        return json.dumps({'error': 'not a valid numerical number'})
    else:
        return meta_dump(meta_id)

@app.route('/api/update')
@app.route('/api/update/:speed_load')
def update_json(speed_load=None):
    if request['REMOTE_ADDR'] == '127.0.0.1':
        reload_config()
        if speed_load == 'full':
            speedy = False
        elif speed_load == 'speedy':
            speedy = True
        else:
            speedy = config.getboolean('Settings', 'speed_load')
        get(delay=config.getint('Settings', 'delay'),
            debug=config.getboolean('Settings', 'debug'), 
            speedy=speedy)
        update()
        return json.dumps(meta, sort_keys=True, indent=4)
    else:
        return json.dumps({'error': 'not authorized to run command'})

@app.route('/repo.json')
@app.route('/api/json')
def raw_json():
    response.headers['Content-Type'] = 'application/json'
    return json.dumps(jdict, sort_keys=True, indent=4)

@app.route('/api/plugins')
def plugin_list():
    response.headers['Content-Type'] = 'application/json'
    items = []
    for item in jdict:
        items.append(item['name'])
    return json.dumps(sorted(items), sort_keys=True, indent=4)

@app.route('/api/plugin/:name')
def plugin_info(name):
    response.headers['Content-Type'] = 'application/json'
    for item in jdict:
        if item['name'] == name:
            return json.dumps(item, sort_keys=True, indent=4)
    return ''

@app.route('/api/categories')
def cat_list():
    response.headers['Content-Type'] = 'application/json'
    cats = []
    for item in jdict:
        for cat in item['categories']:
            if cat not in cats:
                cats.append(cat)
    return json.dumps(sorted(cats), sort_keys=True, indent=4)

@app.route('/api/category/:name')
def cat_info(name):
    response.headers['Content-Type'] = 'application/json'
    cat_name = name.replace('_', ' ')
    items = []
    for item in jdict:
        if cat_name in item['categories']:
            items.append(item['name'])
    return json.dumps(sorted(items), sort_keys=True, indent=4)

@app.route('/api/search', method='POST')
def api_search():
    response.headers['Content-Type'] = 'application/json'
    try:
        field_name = str(request.forms.get('fieldname'))
        action = str(request.forms.get('action'))
        value = str(request.forms.get('value'))
    
        if field_name[:2] == 'v_':
            in_versions = True
            field_name = field_name[2:]
        else:
            in_versions = False

        items = []
        for item in jdict:
            version = {}
            match = False
            if in_versions:
                for version in item['versions']:
                    match = seval(version, field_name, action, value)
            else:
                match = seval(item, field_name, action, value)
            if match:
                items.append(item['name'])
        return json.dumps(items, sort_keys=True, indent=4)
    except:
        return json.dumps({'error': 'Could not perform search'})

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

if __name__ == '__main__':
    reload_config()
    update()
    debug(config.getboolean('Settings', 'debug'))
    run(app=app, 
        port=config.getint('Settings','port'), 
        host=config.get('Settings', 'host'),
 #       server=config.get('Settings', 'server'),
        reloader=config.getboolean('Settings', 'debug'))