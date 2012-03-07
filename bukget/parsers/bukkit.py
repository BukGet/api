import time
import yaml
import json
import re
from StringIO import StringIO
from zipfile import ZipFile
from bukget.parsers.common import BaseParser
from bukget.orm import *

class Parser(BaseParser):
    complete = False
    base_uri = 'http://dev.bukkit.org/server-mods'    
    gen_id = 0
    
    def run(self, gen_id, speedy=True):
        self.get_id = gen_id
        self._server_mods(speedy)
        self.complete = True
    
    
    def _server_mods(self, speedy=True):
        prex = re.compile(r'\/server-mods\/(.*?)\/')
        start = time.time()
        
        curl = self.base_uri
        running = True
        while running:
            count = 0
            page = self._get_page(curl)
            plugins = [a.findChild('a').get('href') for a in page.findAll('h2')]
            for plugin in plugins:
                try:
                    name = prex.findall(plugin)[0]
                except:
                    self._log.debug('Could Not Parse: %s' % plugin)
                else:
                    if self._plugin_update(name):
                        count += 1
            next = page.findAll(attrs={'class': 'listing-pagination-pages-next'})
            if count == 0 and speedy:
                running = False
            elif len(next) > 0:
                link = next[0].findNext('a')
                curl = 'http://dev.bukkit.org%s' % link.get('href')
            else:
                running = False
    
    
    def _plugin_update(self, name):
        new = False
        s = Session()
        
        # The first thing we will need to do is generate the dbo_link and pull the
        # page from DBO.  Once we have that, we can start to pull all of the
        # needed data from the page.
        dbo_link = '%s/%s' % (self.base_uri, name)
        page = self._get_page(dbo_link)
        
        authors = list(set([a.text for a in page.find('li', {'class': 'user-list-item'})\
                                                .findChildren('a', {'class': 'user user-author'})]))
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
            vpage = self._get_page(vurl)

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
                dlpage = self._get_page(v_link)
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
                            dl_data.write(self._get_url(dl_link))
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