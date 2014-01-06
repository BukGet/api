import time
import yaml
import json
import re
import base64
from StringIO import StringIO
from zipfile import ZipFile
import base

log = base.genlog('bukkit') # Generate a log instance for the parser.


def run():
    '''Parser Runtime Function
    Here is where we will be actually running all fo the code below.  This is 
    considered to be boilerplate and should be in every parser.
    '''
    base.run(Parser())


class Parser(base.BaseParser):
    '''Bukkit Parser Object
    '''
    config_type = 'speedy'
    config_dbo_full = False
    config_base = 'http://dev.bukkit.org/bukkit-plugins'
    config_start = 1
    r_vtitle = re.compile(r'size2of3')
    r_version = re.compile(r'\/files\/(.*?)\/')
    r_plugin = re.compile(r'\/(?:server-mods|bukkit-mods|bukkit-plugins)\/(.*?)\/')
    r_versionnum = re.compile(\
        r'b{0,1}\d{1,3}\.{0,1}\d{0,3}\w{0,5}\.{0,1}\d{0,3}\w{0,5}\.{0,1}\d{0,3}\w{0,5}')
    r_stage = re.compile(r'project-stage')
    r_status = re.compile(r'file-status')
    r_filetype = re.compile(r'file-type')
    r_pagenum = re.compile(r'page=(\d{1,4})')
    changes = []

    def _permissions(self, perms):
        '''
        This is a basic function used to normalize out the permissionsn
        contained within the plugin.yml file in a plugin.  As bukkit
        allows for something thats a bit more free-form, we need to
        normalize everything down to something thats a little easier
        to work with and will allow us to search based on the data.

        The end result will use the following format:
        [{
            'role': 'role.permission',
            'default': 'default role value',
        },]

        We will also need to parse the children and apply the default
        values as needed as well.
        '''
        inv = {'op': 'not op', 'not op': 'op', True: False, False: True,
               'OP': 'not op', 'NOT OP': 'op', 'not-op': 'op', 'NOT-OP': 'op'}
        pdict = {}

        # If we run into a string instead of what we expect, then we will
        # convert it into a dict so that the defaults can be applied as
        # expected.
        if isinstance(perms, unicode):
            d = {}
            for item in perms.split():
                d[item] = {}
            perms = d

        for perm in perms:
            # The first thing we need to do is get the role into the pdict
            # dictionary.  Once we have that known we can start working our
            # way down some of the normalizations. Furthermore, we can
            # fix the problem where sometimes we get a null value.
            p = {} if perms[perm] is None else perms[perm]
            if isinstance(p, str): p = {}
            if isinstance(p, unicode): p = {}

            pdict[perm] = {'role': perm}

            if 'default' not in pdict[perm]:
                # If there isnt any default permission currently set, then
                # lets try to parse it out, and return with the default
                # value if we cant find anything.
                if isinstance(p, str) or isinstance(p, bool): 
                    default = p
                else:
                    default = p['default'] if 'default' in p else False
                    default = False if default is None else default
                pdict[perm]['default'] = default
            else:
                # As we may use this if we have children, might as well
                # load it in if we didnt set it ;)
                default = pdict[perm]['default']

            # Lastly lets check for any children.  If we find this entry
            # in the permission, then add in the default option if it
            # doesnt already exist, or if it's different than the
            # default permission set for the parent.
            if 'children' in p and p['children'] is not None:

                # YAIH (Yet Another Interesting Hack) to get around
                # the ambiguous plugin.yml format.
                if isinstance(p['children'], unicode):
                    child_list = p['children'].split()
                else:
                    child_list = p['children']

                for child in child_list:
                    # Nice little hack to get around some ambiguity in
                    # the format.  permissions can be of any number of
                    # different formats.  This is an attempt to
                    # normalize that madness.
                    if isinstance(child, dict):
                        child, value = child.iteritems().next()
                    elif isinstance(p['children'], list) or isinstance(p['children'], unicode):
                        value = False
                    elif isinstance(child, str):
                        dset = child.split(':')
                        if len(dset) > 1:
                            child, value = dset
                        else:
                            child = dset[0]
                            value = False
                    else:
                        value = p['children'][child]

                    # Now lets get a basic structure layed out for the child.
                    if child in pdict:
                        c = pdict[child]
                    else:
                        c = {'default': False, 'role': child}

                    # Once we have that basic structure, lets fix the
                    # permissions if we need to flip it.
                    if 'default' not in c or c['default'] == False:
                        if value:
                            c['default'] = default
                        else:
                            c['default'] = inv[default]
                    pdict[child] = c
        # Lastly, we will convert the dictionary into a list.  As the 
        # list is what we will be using for the Database as well as 
        # the JSON, it only makes sense to do it here ;)
        return [pdict[item] for item in pdict]


    def _commands(self, commands):
        '''
        Function to normalize out the commands into what we expect for 
        bukget.  There isn't nearly as much needed to be done here as
        for the permissions, however it only makes sense to break it
        out just the same.
        '''
        clist = []
        
        # If what were given is not a dictionary, don't even bother to
        # try to parse it, just respond with an empty dictionary.
        if not isinstance(commands, dict):
            return []

        for command in commands:
            c = commands[command]

            # Yet another hack incase there is no data for the command.
            if c is None:
                c = {}

            # This is a bit of a hack to normalize out the aliases so
            # thart it's always a list.  The bukkit plugin.yml format
            # allows for either string or list. however that doesn't
            # exactly jive well with trying to keep a strict format.
            aliases = []
            if 'aliases' in c:
                if isinstance(c['aliases'], list):
                    aliases = c['aliases']

                    # This hack here is to find when ? was used and replace it
                    # with what was expected.
                    if {None: None} in aliases:
                        aliases[aliases.index({None: None})] = '?'
                else:
                    aliases = [str(c['aliases']),]

            if 'permission' in c:
                if isinstance(c['permission'], dict):
                    permission = ''
                else:
                    permission = c['permission']
            else:
                permission = ''

            # Now to add the normalized entry to the clist list.  The
            # clist variable will be whats returned to the calling
            # function.
            clist.append({
                'command': command,
                'aliases': aliases,
                'permission': permission,
                'usage': c['usage'] if 'usage' in c else '',
                'permission-message': c['permission-message'] if 'permission-message' in c else '',
                })
        return clist


    def _find_plugin_yaml(self, dataobj):
        '''
        '''
        yml = False
        try:
            # The first thing we are going to try to do is create a ZipFile
            # object with the StringIO data that we have.
            zfile = ZipFile(dataobj)
        except:
            pass
        else:
            # Before we start recursively jumping through hoops, lets first
            # check to see if the plugin.yml exists at this level.  If so, then
            # just set the yaml variable.  Otherwise we are gonna look for more
            # zip and jar files and dig into them.
            if 'plugin.yml' in zfile.namelist():
                try:
                    yml = yaml.load(zfile.read('plugin.yml'))
                except:
                    return False
            else:
                for filename in zfile.namelist():
                    if not yml and filename[-3:].lower() in ['zip', 'jar']:
                        data = StringIO()
                        yml = self._find_plugin_yaml(\
                            data.write(zfile.read(filename)))
                        data.close()
                zfile.close()
        return yml


    def run(self):
        '''server_mods
        '''
        start = time.time()
        log.info('Starting DBO Parsing at page %s' % self.config_start)

        # So here is the meat and potatos of this function.  We will be looping
        # as long as there is either more changes being added to the changes
        # variable or until we run out of plugins to parse.
        pagenum = self.config_start
        parsing = True
        while parsing:
            count = len(self.changes)   # Current Change count.

            # Lets go ahead and grab the page, then pull out all of the plugins
            # listed on this given page.
            page = self._get_page('%s/?page=%s' % (self.config_base, pagenum))
            plugins = [a.findChild('a').get('href') for a in page.find('table', {'class': 'listing'}).findChildren('h2')]

            # Now to iterate through all of the plugins we discovered...
            for plugin in plugins:
                try:
                    # Here we are attemping to pull out the plugin slug.  This
                    # will be used as
                    slug = self.r_plugin.findall(plugin)[0]
                except:
                    log.debug('Could not parse %s' % plugin)
                else:
                    self.plugin(slug)
            if page.find(attrs={'class': 'listing-pagination-pages-next'}):
                pagenum += 1
            else:
                parsing = False
            if len(self.changes) == count and self.config_type == 'speedy' and not self.config_dbo_full:
                parsing = False
            else:
                log.info('Parsing DBO Page %s' % pagenum)

        # The geninfo for this generation.
        geninfo = {
            'duration': int(time.time() - start),
            'timestamp': int(time.time()),
            'parser': 'bukkit',
            'type': self.config_type,
            'changes': self.changes,
        }

        # Lets send a log and then upload the generation info to the API.
        log.info('DBO Parsing complete. Time: %s' % geninfo['duration'])
        self._add_geninfo(geninfo)


    def plugin(self, slug):
        '''plugin slug
        '''

        # The first thing we need to do here is query the API and find out if
        # the plugin already exists.  If it doesn't then we will start with a
        # completely clean dictionary.
        plugin = self._api_get({'server': 'bukkit', 'slug': slug})
        if not plugin:
            plugin = {
                'slug': slug,
                'server': 'bukkit',
                'description': '',
                'authors': [],
                'categories': [],
                'versions': [],
                'plugin_name': '',
            }
            log.info('Adding Bukkit Plugin %s' % slug)
        changes = len(self.changes)
        porig = plugin
        
        yml = False         # Variable to house the most recent version yaml.
        running = True      # Will stay true as long as we are parsing versions
        filepage = 1        # The current page of versions.
        versions = []       # The versions list.
        while running and self.config_type != 'stage_update':
            page = self._get_page('%s/%s/files/?page=%s' % (self.config_base, slug, filepage))
            try:
                rows = page.findChild('tbody').findAll('tr')
            except:
                rows = []
            for row in rows:
                vlink = row.findNext('td', {'class': 'col-file'}).findNext('a').get('href')
                vslug = self.r_version.findall(vlink)[0]
                tyml, vdata = self.version(slug, vslug)
                if vdata is not None:
                    versions.append(vdata)
                if not yml:
                    yml = tyml
            if page.find('li', {'class': 'listing-pagination-pages-next'}) is not None:
                filepage += 1
            else:
                running = False
        if not yml:
            yml = {}


        # Before we bother to get too much further, lets make sure there are
        # actually plugin revisions uploaded to DBO.  If there isn't, then there
        # isn't too much of a new to import this into the API.  Furthermore, we
        # need to check to make sure that the plugin hasnt been deleted and the
        # references on BukkitDev just havent bheen updated yet.  Also if the
        # project has been deleted, then we should clean it up in the database.

        # First lets scrape out everything we need from the plugins main page.
        # Some of these will be overrided by the YAML settings, so it's easier
        # to pre-load here and then opverload if needed.
        page = self._get_page('%s/%s' % (self.config_base, slug))

        # If the plugin has been deleted, then shortcut everything and tell the
        # base parser to just delete the entry.
        if len(page) < 1:
            return self._delete_plugin(plugin)
        elif 'deleted' in plugin:
            del(plugin['deleted'])
        if page == 'There was an error with cookies, please try again.':
            return self._delete_plugin(plugin)
        
        # Lets get the Curse_id.  This requires us to follow the curse link and
        # pull up their page to get the ID.
        try:
            plugin['curse_link'] = page.find('li', {'class': 'curse-tab'})\
                                       .findChild('a').get('href')
            cursepage = self._get_page(plugin['curse_link'])
            plugin['curse_id'] = int(cursepage.find('li', {'class': 'grats'})\
                                              .findChild('span').get('data-id'))
        except AttributeError:
            pass

        # Plugin Stage
        plugin['stage'] = page.find('span', {'class': self.r_stage}).text
        plugin['authors'] = list(set([a.text for a in page.find('li', {'class': 'user-list-item'})\
                                                .findChildren('a', {'class': 'user user-author'})]))
        plugin['categories'] = [a.text for a in page.findAll('a', {'class': 'category'})]
        try:
            plugin['logo'] = page.find('a', attrs={'class': 'project-default-image'})\
                                 .findChild('img').get('src')
            plugin['logo_full'] = page.find('a', attrs={'class': 'project-default-image'})\
                                      .findChild('img').get('data-full-src')
        except:
            plugin['logo'] = ''
            plugin['logo_full'] = ''

        # Now to pull in all of the data from the YAML definitions.
        if 'name' in yml: plugin['plugin_name'] = yml['name']
        if 'main' in yml: plugin['main'] = yml['main']
        if 'description' in yml: plugin['description'] = yml['description']
        if 'author' in yml: 
            if isinstance(yml['author'], list): 
                plugin['authors'] = yml['author']
            else:
                plugin['authors'] = [yml['author'],]
        if 'authors' in yml: 
            if isinstance(yml['authors'], list):
                plugin['authors'] = yml['authors']
            else:
                plugin['authors'] = [yml['authors'],]
        if 'website' in yml: 
            plugin['website'] = yml['website']
        else:
            plugin['website'] = '%s/%s' % (self.config_base, slug)

        # This solves what I have called the 'dean79' issue.  Basically people
        # who have no understanding how to peroperly format a list in their
        # plugin.yml.
        authors = []
        for author in plugin['authors']:
            if isinstance(author, list):
                [authors.append(a) for a in author]
            else:
                authors.append(author)
        plugin['authors'] = authors

        # These don't really require any work, as we can determine these without
        # parsing either the YAML or scraping it out of the page.
        plugin['dbo_page'] = '%s/%s' % (self.config_base, slug)
        plugin['versions'] = versions

        # Here are some last minute re-classifications to make sure we are
        # sending the right data to the API.
        plugin['description'] = unicode(plugin['description']).encode('ascii', 'replace')

        # This is a quick check to see if there is a improper version condition
        # with this plugin.  If there is, we will then rely on the dbo_version
        # instead of the version.  dbo_version is more unreliable however, so
        # we don't want to use it unless we have to.
        vitems = [v['version'] for v in versions]
        if len(vitems) > 2 and len(set(vitems)) == 1:
            if '_use_dbo' not in plugin:
                log.info('Can no longer trust %s\'s plugin.yml version...' % plugin['slug'])
                plugin['_use_dbo'] = True
                v2 = []
                for version in versions:
                    if version['dbo_version'] is not None:
                        version['version'] = version['dbo_version']
                    v2.append(version)
                plugin['versions'] = v2


        # Lastly, we only want to even bother to commit this up if there is at
        # least 1 version of the plugin uploaded.
        if len(versions) > 0:
            if self.config_type == 'stage_update':
                self._update_status(plugin)
            else:
                self._update_plugin(plugin)


    def version(self, plugin, slug):
        '''version plugin slug
        '''
        # The very first thing we need to do if check to see if this version
        # already exists in the API.
        version = None
        p = self._api_get({'slug': plugin,
                           'server': 'bukkit',
                           'versions.slug': slug})
        if p is not None:
            version = ([v for v in p['versions'] if v['slug'] == slug])[0]
        else:
            p = self._api_get({'slug': plugin, 'server': 'bukkit'})
            if p == None: p = {}
        if version:
            if self.config_type == 'speedy': 
                return False, version
            log.info('Updating Bukkit Plugin %s Version %s' % (plugin, slug))
        else:
            version = {
                'slug': slug,
            }
            log.info('Adding Bukkit Plugin %s Version %s' % (plugin, slug))

        # Now we need to pull the page.  While we are at it, we might as well
        # parse as much out of the page as we can.
        dbo_page = '%s/%s/files/%s/' % (self.config_base, plugin, slug)
        page = self._get_page(dbo_page)

        # Simple hack to break out of parsing the page any further if we are
        # getting empty data back from _get_page.  This should stop a lot of
        # empty parsing.
        if len(page) < 1:
            return {}, None
        
        try:
            # Here we are going to try to pull out the DBO Version on the page.
            # Yes this is pretty hackish, however its needed as it's the only
            # way I have found to reliably pull out the proper versioning
            version['dbo_version'] = self.r_versionnum.findall(\
                page.find(attrs={'class': self.r_vtitle}).findNext('h1').text)[0]
            if version['dbo_version'][-4:].lower() == '.jar':
                version['dbo_version'] = version['dbo_version'][:-4]
        except:
            version['dbo_version'] = None
        version['link'] = dbo_page
        version['date'] = int(page.find(attrs={'class': 'standard-date'}).get('data-epoch'))
        version['download'] = page.find('dt', text='Filename').findNext('a').get('href')
        version['file_id'] = int(''.join(version['download'].split('/')[5:7]))
        version['filename'] = page.find('dt', text='Filename').findNext('a').text
        version['md5'] = page.find('dt', text='MD5').findNext('dd').text
        version['status'] = page.find(attrs={'class': self.r_status}).text
        version['type'] = page.find(attrs={'class': self.r_filetype}).text
        version['game_versions'] = list(set([a.text for a in page.find('dt', text='Game version')\
                                                                 .findNext('ul')\
                                                                 .findChildren('li')]))
        try:
            version['changelog'] = base64.encodestring(\
                page.find('h3',text='Change log').findParent('div').prettify())
        except:
            version['changelog'] = ''

        # Lets also pre-populate some information into the version to make sure
        # that regardless, we will have something in these values.
        version['hard_dependencies'] = []
        version['soft_dependencies'] = []
        version['commands'] = []
        version['permissions'] = []

        # Now that we have parsed out some of the information, we need to do a
        # little sanity check and make sure that we only input zip or jar files
        # into the API.  All the other stuff, while useful, is outside the
        # scope of what the API is intended for.
        if version['download'][-3:] not in ['jar', 'zip']:
            return False, None

        # Next we need to download the plugin and try to get to the jar file.
        # we will be using a separate function to handle this that can
        # recursively drill in until it finds a plugin.yml file.  If no yaml
        # file was found, then we will just throw a blank dictionary into the
        # variable in order to get through the if block.
        download = StringIO()
        download.write(self._get_url(version['download']))
        yml = self._find_plugin_yaml(download)
        download.close()
        if not yml: yml = {}

        # Now to populate the version dictionary based on the plugin.yml ;)
        if 'depend' in yml and yml['depend'] is not None: 
            version['hard_dependencies'] = yml['depend']
        if 'softdepend' in yml and yml['softdepend'] is not None:
            version['soft_dependencies'] = yml['softdepend']
        if 'commands' in yml and yml['commands'] is not None:
            try:
                version['commands'] = self._commands(yml['commands'])
            except:
                log.warn('Could not Parse commands for %s:%s' % (plugin, slug))
                version['commands'] = []
        if 'permissions' in yml and yml['permissions'] is not None:
            try:
                version['permissions'] = self._permissions(yml['permissions'])
            except:
                log.warn('Could not Parse permissions for %s:%s' % (plugin, slug))
                version['permissions'] = []
        if 'version' in yml and yml['version'] is not None:
            version['version'] = unicode(yml['version']).encode('ascii', 'replace')


        # This is a last-minute hack to check to see if we prefer the dbo
        # version over the plugin.yml version.  If this is the case, then we
        # have to override the version definition with the dbo_version def.
        if '_use_dbo' in p or 'version' not in version: 
            version['version'] = version['dbo_version']

        self.changes.append({'plugin': plugin, 'version': version['version']})
        return yml, version