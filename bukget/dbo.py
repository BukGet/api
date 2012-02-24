import yaml
import config
import json
import re
import os
from zipfile import ZipFile
from StringIO import StringIO
from urllib2 import urlopen
from sqlalchemy.orm import joinedload, sessionmaker
from sqlalchemy import desc, create_engine
from orm import *
from BeautifulSoup import BeautifulSoup as bsoup
    
_timer = datetime.datetime.now()

def plugin_cache():
    s = Session()
    data = s.query(Plugin).options(joinedload('versions')).all()
    s.close()
    return data

def meta_cache():
    s = Session()
    data = s.query(Meta).options(joinedload('history'))\
                            .order_by(desc(Meta.id)).limit(1).one()
    s.close()
    return data

def category_cache():
    s = Session()
    plugins = s.query(Plugin).all()
    data = []
    for plugin in plugins:
        for category in plugin.get('categories'):
            if category not in data:
                data.append(category)
    s.close()
    return data

def update_sqlite():
    sqlite = create_engine('sqlite:///static/cache_gen.db')
    Maker = sessionmaker(sqlite)
    Plugin.metadata.create_all(sqlite)
    Version.metadata.create_all(sqlite)
    s = Session()
    db = Maker()
    plugins = s.query(Plugin).all()
    for plugin in plugins:
        pid = plugin.id
        s.expunge(plugin)
        plugin = db.merge(plugin)
        db.commit()
        versions = s.query(Version).filter_by(plugin_id=pid).all()
        for version in versions:
            s.expunge(version)
            db.merge(version)
        db.commit()
    s.close()
    db.close()
    os.remove('static/cache.db')
    os.rename('static/cache_gen.db', 'static/cache.db')

def update(speedy=True):
    conf = config.Configuration()
    updated = False
    updater = None
    for parent in conf.parents:
        if not updated:
            updated = _child_update(parent)
            if updated:
                updater = parent
    if not updated and conf.is_parent:
        _parent_update(speedy)
    if updated:
        return {'type': 'child', 'parent': updater, 'status': 'ok'}
    elif conf.is_parent:
        return {'type': 'parent', 'status': 'ok'}
    else:
        return {'type': 'child', 'status': 'failed'}
            
def _child_update(parent):
    try:
        meta = json.loads(urlopen('http://%s/api' % parent).read())
        jdict = json.loads(urlopen('http://%s/api/json' % parent).read())
    except:
        return False
    s = Session()
    
    if len(s.query(Meta).filter_by(id=meta['id']).all()) >= 1:
        s.close()
        return True
    
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
    for jplugin in jdict:
        try:
            plugin = s.query(Plugin).finter_by(name=jplugin['name']).one()
        except:
            plugin = Plugin(jplugin['name'],
                            jplugin['authors'],
                            jplugin['categories'],
                            jplugin['bukkitdev_link'],
                            jplugin['status'],
                            jplugin['plugin_name'],
                            jplugin['desc'])
            s.add(plugin)
            s.commit()
        for jversion in jplugin['versions']:
            if len(s.query(Version).filter_by(plugin_id=plugin.id,
                                              md5=jversion['md5']).all()) < 1:
                ver = Version(jversion['name'], 
                              datetime.datetime.fromtimestamp(jversion['date']),
                              jversion['dl_link'],
                              jversion['game_builds'],
                              jversion['filename'],
                              jversion['md5'],
                              jversion['soft_dependencies'],
                              jversion['hard_dependencies'],
                              plugin.id,
                              jversion['status'],
                              jversion['type'])
                s.add(ver)
                s.commit()
    update_sqlite()
    return True

def _parent_update(speedy):
    conf = config.Configuration()
    start = datetime.datetime.now()
    s = Session()
    
    # Here we instantiate and add the metadata row to the database.  We will
    # be using this for historical reasons and will need the id for the
    # history rows.
    meta = Meta()
    s.add(meta)
    s.commit()
    
    prex = re.compile(r'\/server-mods\/(.*?)\/')
    
    url = 'http://dev.bukkit.org/server-mods'
    plugins = []
    
    curl = url
    phase1 = True
    while phase1:
        count = 0
        page = _get_page(curl, conf.delay)
        plugins = [a.findChild('a').get('href') for a in page.findAll('h2')]
        for plugin in plugins:
            try:
                name = prex.findall(plugin)[0]
            except:
                if conf.debug:
                    print 'Could Not Parse: %s' % plugin
            else:
                if _plugin_update(name, meta):
                    count += 1
        next = page.findAll(attrs={'class': 'listing-pagination-pages-next'})
        if count == 0 and speedy:
            phase1 = False
        elif len(next) > 0:
            link = next[0].findNext('a')
            curl = 'http://dev.bukkit.org%s' % link.get('href')
        else:
            phase1 = False
            
    # Lastly, we will update the meta object to get the time it took to run
    # the generation and then merge the update.
    meta.finish()
    s.merge(meta)
    s.commit()
    s.close()
    update_sqlite()

def _get_page(url, delay=2):
    conf = config.Configuration()
    global _timer
    while (datetime.datetime.now() - _timer).seconds < delay:
        time.sleep(.25)
    _timer = datetime.datetime.now()
    if conf.debug:
        print 'Fetching: %s' % url
    return bsoup(urlopen(url).read())

def _plugin_update(name, meta):
    conf = config.Configuration()
    new = False
    s = Session()
    
    # The first thing we will need to do is generate the dbo_link and pull the
    # page from DBO.  Once we have that, we can start to pull all of the
    # needed data from the page.
    dbo_link = 'http://dev.bukkit.org/server-mods/%s/' % name
    page = _get_page(dbo_link, conf.delay)
    
    authors = list(set([a.text for a in page.findAll('a', {'class': 'user user-author'})]))
    categories = [a.text for a in page.findAll('a', {'class': 'category'})]
    status = page.find('span', {'class': re.compile(r'project-stage')}).text
    plugin_name = page.find('div', {'class': 'global-navigation'}).findNextSibling('h1').text
    plugin_desc = page.find('div', {'class': 'content-box-inner'}).text
    
    # This is a bit of a hack to see if the plugin_name will properly export 
    # to json, if not, then we will need to simply dump it.
    try:
        json.dumps(plugin_name)
    except:
        plugin_name = ''
    
    # Here we will try to update the plugin in the database.  If that fails
    # for any reason (i.e. it doesn't exist) we will then add a new plugin to
    # the database.
    try:
        plugin = s.query(Plugin).filter_by(name=name).one()
        plugin.update(authors=authors, categories=categories, 
                      status=status, plugin_name=plugin_name,
                      desc=plugin_desc)
        s.merge(plugin)
    except:
        plugin = Plugin(name, authors, categories, dbo_link, status, 
                        plugin_name, plugin_desc)
        s.add(plugin)
    s.commit()
    
    # Now we will drill into the specific versions.  For that we will need to
    # parse the files table on the files page.  Here we will be generating the
    # link and pulling the page down.
    vurl = '%sfiles/' % dbo_link
    more_versions = True
    while more_versions:
        vcount = 0
        vpage = _get_page(vurl, conf.delay)
    
        try:
            rows = vpage.findChild('tbody').findAll('tr')
        except:
            rows = []
    
        for row in rows:
            # Here we are parsing through the version table and trying to pull out
            # all of the relevent information for each version.  We are handling
            # all of this from the table instead of on the individual file page
            # as all of the information we need is here already.  We will still
            # need the file page however for the raw download link as that is not
            # contained here.
            v_flnk = row.findNext('td', {'class': 'col-file'}).findNext('a')
            v_type = row.findNext('span', {'class': re.compile(r'file-type')}).text
            v_stat = row.findNext('span', {'class': re.compile(r'file-status')}).text
            v_rdate = row.findNext('span', {'class': 'standard-date'}).get('data-epoch')
            v_gbvs = [a.text for a in row.findNext('td', {'class': 'col-game-version'})\
                                        .findChildren('li')]
            v_file = row.findNext('td', {'class': 'col-filename'}).text.strip()
            
            # This has to be disabled as its no longer on the page.  Instead
            # we are now forced to parse every single download page.  Thanks
            # Curse for 
            #v_md5 = row.findNext('td', {'class': 'col-md5'}).text
            v_link = 'http://dev.bukkit.org%s' % v_flnk.get('href')
            v_name = v_flnk.text
            v_date = datetime.datetime.fromtimestamp(float(v_rdate))
        
            # If the file that we are parsing is not a zip or a jar file, then
            # there is no reason to continue processing.
            if len(v_file.split('.')) > 1:
                if v_file.split('.')[-1].lower() not in ['zip','jar']:
                    continue
        
            #try:
            #    version = s.query(Version).filter_by(plugin_id=plugin.id, 
            #                                         name=name).one()
            #except:
            #    new = True
            dlpage = _get_page(v_link)
            v_md5 = dlpage.find('dt', text='MD5').findNext('dd').text
            dl_link = dlpage.findChild(attrs={
                                'class': 'user-action user-action-download'})\
                            .findNext('a').get('href')
            try:
                version = s.query(Version).filter_by(md5=v_md5).one()
            except:
                vcount += 1
            
                s_deps = []
                h_deps = []
            
                # Now we will try to determine the hard and soft dependencies.  We
                # will do this by opening up into the jar file and pulling out the
                # plugin.yml that is required for all plugins in bukkit.
                try:
                    if v_file.split('.')[-1].lower() == 'jar':
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
                        jar.close()
                        dl_data.close()
                except:
                    pass
            
                # Lastly we need to add this version to the database as well as
                # the associated history element.
                s.add(Version(v_name, v_date, dl_link, v_gbvs, v_file, v_md5,
                              s_deps, h_deps, plugin.id, v_stat, v_type))
                s.add(History(meta.id, plugin.name, v_name))
                s.commit()
        
        # Now we need to fetch the next page url if it is available.  If there
        # is no next page to goto, then we will set more_versions to false.
        if vcount > 0:
            new = True
            try:
                link = vpage.find('li', {'class': 'listing-pagination-pages-next'})
                vurl = 'http://dev.bukkit.org%s' % link.findChild('a').get('href')
            except:
                more_versions = False
        else:
            more_versions = False
        
        
    # Just some final cleanup here.  If we found any new versions, then return
    # True, else return False.
    s.close()
    return new
