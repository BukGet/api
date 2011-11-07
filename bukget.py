#!/usr/bin/env python
import os

#### CONFIGURATION AND PRE-PROCESSING
# The script has to run from the location on disk that it lives.
#os.chdir(os.path.dirname(__file__))

# Activate the virtualenv
#activate_this = '../bin/activate_this.py' % ENV
#execfile(activate_this, dict(__file__=activate_this))

# Now we can load in whatever libaries we need as we are not inside the
# virtualenv.
from sqlalchemy import (Table, Column, Integer, String, DateTime, Date, 
                        ForeignKey, Text, Boolean, MetaData, 
                        and_, desc)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
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
config = ConfigParser()

sql_string = 'sqlite:///database.db'
engine = create_engine(sql_string)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Plugin(Base):
    __tablename__ = 'plugin'
    id = Column(Integer(8), primary_key=True)
    name = Column(String(128), unique=True)
    categories = Column(Text)
    authors = Column(Text)
    status = Column(String(32))
    link = Column(Text)
    versions = relationship('Version', backref='plugin')
    
    def __init__(self, name, authors, categories, link, status):
        self.name = name
        self.link = link
        self.update(authors=authors, categories=categories, status=status)
    
    def _list_parser(self, slist):
        if isinstance(slist, unicode):
            data = slist.split(',')
        else:
            data = slist
        vals = []
        for item in data:
            vals.append(item.strip())
        return vals
    
    def update(self, authors=None, categories=None, status=None):
        if authors is not None:
            self.authors = ', '.join(self._list_parser(authors))
        if categories is not None:
            self.categories = ', '.join(self._list_parser(categories))
        if status is not None:
            self.status = status
    
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
        if isinstance(slist, unicode):
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

def get(delay=2, host='http://dev.bukkit.org', debug=False, speedy=False):
    s = Session()
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
                plugin = Plugin(name, authors, categories, link, status)
                s.add(plugin)
            plugin.update(authors=authors, categories=categories, 
                          status=status)
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
                    s.add(version)
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
    s.close()

def dump(debug=False):
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
                'game_builds': [int(i) for i in version.get('cb_versions')],
                'soft_dependencies': version.get('soft_dependencies'),
                'hard_dependencies': version.get('hard_dependencies')
            })
        jdata.append({
            'name': plugin.name,
            'bukkitdev_link': plugin.link,
            'status': plugin.status,
            'authors': plugin.get('authors'),
            'categories': plugin.get('categories'),
            'versions': versions
        })
    return json.dumps(jdata, sort_keys=True, indent=4)

def update():
    global jdict
    jdict = json.loads(dump())

def reload_config():
    config.read('bukget.ini')

@app.route('/')
@app.route('/index.html')
def home_page():
    return template('home_page')

@app.route('/api/update')
def update_json():
    if request['REMOTE_ADDR'] == '127.0.0.1':
        reload_config()
        get(delay=config.getint('Settings', 'delay'),
            debug=config.getboolean('Settings', 'debug'), 
            speedy=config.getboolean('Settings', 'speed_load'))
        update()

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

@app.route('/ai/categories')
def cat_list():
    response.headers['Content-Type'] = 'application/json'
    cats = []
    for item in jdict:
        for cat in item['categories']:
            if cat not in cats:
                cats.append(cat)
    return json.dumps(cats, sort_keys=True, indent=4)

@app.route('/api/category/:name')
def cat_info(name):
    cat_name = name.replace('_', ' ')
    items = []
    for item in jdict:
        if cat_name in item['categories']:
            items.append(item['name'])
    return json.dumps(items, sort_keys=True, indent=4)

@app.route('/api/search', method='POST')
def api_search():
    field_name = request.forms.get('field_name')
    action = request.forms.get('action')
    value = request.forms.get('action')
    
    if field_name[:1] == 'v_':
        in_versions = True
        field_name = field_name[2:]
    else:
        in_versions = False
    
    items = []
    for item in jdict:
        match = False
        if in_versions:
            for version in item['versions']:
                match = seval(version, field_name, action, value)
        else:
            match = seval(item, field_name, action, value)
        if match:
            items.append(item)
    return json.dumps(items, sort_keys=True, indent=4)

def seval(item, name, action, value):
    if name in item:
        try:
            if action == '=':
                if value == item[name]:
                    return True
            if action == '<':
                if value < item[name]:
                    return True
            if action == '<=':
                if value <= item[name]:
                    return True
            if action == '>':
                if value > item[name]:
                    return True
            if action == '>=':
                if value >= item[name]:
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
        host=config.get('Settings', 'host'))