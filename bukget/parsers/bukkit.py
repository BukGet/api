import time
import yaml
import json
import re
import datetime
import bukget.db as db
from bukget.log import log
from bukget.parsers.base import BaseParser
from StringIO import StringIO
from zipfile import ZipFile


class Parser(BaseParser):
    # This is the Bukkit Parser class.  This is the class that will actually
    # parse out the data from DBO and dump it into the database.
    
    # This is the base uri that we will be parsing from.
    base_uri = 'http://dev.bukkit.org/server-mods'

    # This is the regex that we will be using to parse out the url slug that is
    # used for bukkit.
    prex = re.compile(r'\/server-mods\/(.*?)\/')

    # This is the regex that is used to parse out the version slug that is used
    # for bukkit.
    vrex = re.compile(r'\/files\/(.*?)\/')

    # This is the regex that we will be using for parsing out the version
    # numbers.
    revex = re.compile(r'b{0,1}\d{1,3}\.{0,1}\d{0,3}\w{0,5}\.{0,1}\d{0,3}\w{0,5}\.{0,1}\d{0,3}\w{0,5}')

    # This regex is used to parse out the plugin status.
    restage = re.compile(r'project-stage')

    # This regex is used to pull the file status for versions.
    refilest = re.compile(r'file-status')

    # This regex is used to pull the file type for versions.
    refilety = re.compile(r'file-type')


    def run(self, speedy=True, page_num=1):
        '''run speedy=True
        This function is the main function to launch the parser.  The speedy
        flag denoted whether the parser will run through the entire DBO database
        or will only check for those items it does not have in the database.
        '''
        self.complete = False
        self._server_mods(speedy, page_num)
        self.complete = True


    def _server_mods(self, speedy, page_num):
        '''_server_mods speedy=True
        This function is what will be parsing the plugin listing pages, looking
        for new plugins.
        '''
        # Here we set a few things up, we will get the current time in order
        # to set the duration for the meta object, instantiate a database
        # session, and lastly create a Meta object that we will be using.
        start = time.time()
        s = db.Session()
        self.meta = db.Meta('bukkit')
        s.add(self.meta)

        # Here we will be pre-loading the current url (curl) variable and
        # setting running to True so that the while loop will just keep doing
        # it's thing.
        curl = '%s?page=%s' % (self.base_uri, page_num)
        running = True

        while running:
            # This counter keeps track of the number of plugins that we have
            # modified.  This is very useful in speedy mode as if we run through
            # a whole page without any plugin changes, there is generally no
            # need to keep going.
            count = 0

            page = self._get_page(curl)

            # Here we are building a list of all of the plugin links on the page
            # so that we can parse out the plugin slug and hand that off to the
            # _plugin function.
            plugins = [a.findChild('a').get('href') for a in page.findAll('h2')]

            for plugin in plugins:

                # Here we will attempt to parse out the plugin name.  If we are
                # unable to do so for any reason, then we simply log it and
                # move on.
                try:
                    name = self.prex.findall(plugin)[0]
                except:
                    log.debug('Could not Parse: %s' % plugin)
                else:
                    # Now we marge in any changes from the _plugin function into
                    # the database
                    count += self._plugin(name)

            # Next we need to find the link to the next page, then set the curl
            # variable to the next page we will need to parse.
            nurl = page.findAll(attrs={'class': 'listing-pagination-pages-next'})
            if len(nurl) > 0:
                link = nurl[0].findNext('a')
                curl = 'http://dev.bukkit.org%s' % link.get('href')
            else:
                running = False

            # Lastly we will need to check the count and if we are running in
            # speedy mode and act accordingly.
            if count == 0 and speedy:
                running = False

        # Now for a little cleanup, we will commit then close the database
        # session and jump for joy!
        s.merge(self.meta)
        s.commit()
        s.close()


    def _plugin(self, name):
        '''_plugin name
        This function parses the plugin page and subsiquent files pages to pull
        all of the information from DBO and update the plugin cache we have in
        the database.  We will then return both the cound of changes and the
        updated plugin object.
        '''
        count = 0       # This counter keeps track of the number of updates.
        # First things first, we will need to create a session from the reactor
        # and then check to see if this is an existing plugin or not.  If not,
        # then we will need to create a new one.
        s = db.Session()
        try:
            plugin = s.query(db.Plugin).filter_by(name=name).one()
            log.debug('PARENT: Updating plugin %s in bukkit repository' % name)
        except:
            plugin = db.Plugin(name, 'bukkit')
            s.add(plugin)
            log.info('PARENT: Adding plugin %s in bukkit repository' % name)
            count += 1

        # Next thing we need to do is build the dbo link.  This is the uri that
        # points directly to the plugin.
        plugin.link = '%s/%s' % (self.base_uri, name)

        # Now to pull the page down.
        page = self._get_page(plugin.link)

        # Next we will be parsing through the authors.  If we run into an author
        # that we havent seen before, then we will also add that author to the
        # database as well.
        authors = list(set([a.text for a in page.find('li', {'class': 'user-list-item'})\
                                                .findChildren('a', {'class': 'user user-author'})]))
        for author_name in authors:
            try:
                author = s.query(db.Author).filter_by(name=name).first()
            except:
                author = db.Author(author_name)
                s.add(author)
                s.commit()

            if author not in plugin.authors:
                plugin.authors.append(author)

        # and for the next fun item, categories!  We will be performing the 
        categories = [a.text for a in page.findAll('a', {'class': 'category'})]
        for cat_name in categories:
            try:
                category = s.query(db.Category).filter_by(name=cat_name).first()
            except:
                category = db.Category(cat_name)
                s.add(category)
                s.commit()

            if category not in plugin.categories:
                plugin.categories.append(category)

        # Now for some easier stuff, we will be parsing through the status,
        # the plugin's full name, and the plugin description.
        plugin.stage = page.find('span', {'class': self.restage}).text
        #if plugin.description == None:
        #    plugin.description = page.find('div', {'class': 'content-box-inner'}).text[:150]
        plugname = page.find('div', {'class': 'global-navigation'}).findNextSibling('h1').text

        # This is a bit of a hack to get around some issues that have cropped up
        # thanks to plugins using unicode characters that just arent handled in
        # json.  Once we have a determination of what we can do, we will
        # populate that into the plugin.
        try: 
            json.dumps(plugname)
        except: 
            plugname = ''
        #if plugin.plugname == None:
        #    plugin.plugname = plugname

        # Now we need to merge the changes made and commit them into the
        # database before we go much further.  We will also close out the
        # session at this point because there will be no further changes to the
        # plugin object at this point.
        plugin = s.merge(plugin)
        s.commit()

        # Next we need to start working our way through the various versions.
        # This will be handled very much in the same way as how we were handling
        # plugins, by simply looking for the version slug and handing this
        # information off to a seperate function designed to better break down
        # the data.

        # Here we start out (just like before) by pre-loading the vurl variable
        # and setting the running flag to true.  We will also keep track of the
        # number of changes in order to speed things up a bit.
        vurl = '%s/files/' % plugin.link
        running = True

        while running:
            changes = 0     # Counter to keep track of changes on this page.
            # We start off by pulling down the files page and parsing out the 
            # link to the version page.  Then we will hand off that slug with
            # the plugin.id so that the _version function knows what to do from
            # there.
            vpage = self._get_page(vurl)

            # Lets try to parse out the rows in the table on the page.  If we
            # can't find anything, then just set the rows variable to an empty
            # list so we can drop out of the loop gracefully.
            try:
                rows = vpage.findChild('tbody').findAll('tr')
            except:
                rows = []


            self.ymlname = False
            self.ymldesc = False
            for row in rows:
                #try:
                vlink = row.findNext('td', {'class': 'col-file'}).findNext('a').get('href')
                vtxt = row.findNext('td', {'class': 'col-file'}).findNext('a').text
                slug = self.vrex.findall(vlink)[0]
                try:
                    vname = self.revex.findall(vtxt)[0]
                except:
                    vname = vtxt
                changes += self._version(plugin, slug, vname)
                #except:
                #    pass

            # Now we will add the changes count into the count counter.  This
            # allows us to keep better track of the number of changes that had
            # occured.
            count += changes

            # Now we will try to find the next files page if we detected any
            # outstanding changes on this one.  We will keep drilling down until
            # we have hit all of the pages or if no more changes exist.
            if changes > 0:
                try:
                    link = vpage.find('li', {'class': 'listing-pagination-pages-next'})
                    vurl = 'http://dev.bukkit.org%s' % link.findChild('a').get('href')
                except:
                    running = False
            else:
                running = False


        # Now we will check to see if we got any plugin names or descriptions
        # from the plugin.yml parsing in the version and apply those changes
        # if we did.
        if self.ymlname:
            log.debug('PARENT: Overloading %s plugname to %s' % (plugin.name, self.ymlname))
            plugin.plugname = self.ymlname
        if self.ymldesc:
            log.debug('PARENT: Overloading %s description to %s' % (plugin.name, self.ymldesc))
            plugin.description = self.ymldesc
        s.merge(plugin)

        # Lastly, we will return the number of changes that we made and close
        # the database session.
        s.commit()
        s.close()
        return count


    def _version(self, plugin, slug, name):
        '''_version plugin_id slug
        The version vunction is designed to take the URL slug and plugin id and
        will update the database if necessary with new version information for
        that plugin.
        '''
        # We start off with the usual setup stuff, instantiating a counter for
        # tracking any changes, instantiating a new database session, the normal
        # boring stuff we always have to do.  We are also computing the version
        # link.  We will also use this link ourselves to pull the rest of the 
        # information we need.
        changes = 0
        build = False
        link = '%s/%s/files/%s' % (self.base_uri, plugin.name, slug)
        s = db.Session()

        # The first thing we need to do is check to see if we even have this
        # version in the database.  If we do, then we don't need to do anything.
        try:
            version = s.query(db.Version).filter_by(link=link).one()
            s.close()
            return changes
        except:
            # Generally we will end up here, this is ok, because this means that
            # we have to parse the version and commit it to the database.
            version = db.Version(name, plugin.id)
            log.info('PARENT: Adding version %s for plugin %s for bukkit repository' % (name, plugin.name))
            
            # as we need this, let go ahead and add the link.
            version.link = link

            # Yay the page!
            page = self._get_page(version.link)

            # This is the epoch date that the file was uploaded on.  We will use
            # this when adding it into the db.
            epoch = page.find(attrs={'class': 'standard-date'}).get('data-epoch')

            # Now we start parsing!
            version.download = page.find('dt', text='Filename').findNext('a').get('href')
            version.filename = page.find('dt', text='Filename').findNext('a').text
            version.md5 = page.find('dt', text='MD5').findNext('dd').text
            version.date = datetime.datetime.fromtimestamp(float(epoch))
            version.status = page.find(attrs={'class': self.refilest}).text
            version.type = page.find(attrs={'class': self.refilety}).text
            version.game_versions = list(set([a.text for a in page.find('dt', text='Game version')\
                                                                  .findNext('ul')\
                                                                  .findChildren('li')]))

            # For the rest of the information, we will need to download the
            # plugin itself and parse that information.
            if version.download[-3:].lower() == 'jar':
                # The first thing we need to do with this jar file is to
                # download it and instantiate the data as a ZipFile object.
                # From there we can pull out the needed data and parse it as
                # needed.
                data = StringIO()
                try:
                    data.write(self._get_url(version.download))
                    jar = ZipFile(data)
                except:
                    jar = ZipFile(StringIO(), 'w')

                # Now we will look for the plugin.yml file inside the jarfile
                # and will also add in the hard & soft dependencies, commands,
                # and permissions.
                version.hard_dependencies = []
                version.soft_dependencies = []
                version.commands = {}
                version.permissions = {}
                if 'plugin.yml' in jar.namelist():
                    try:
                        config = yaml.load(jar.read('plugin.yml'))
                    except:
                        config = {}
                    
                    # Hard Dependencies
                    if 'depend' in config and config['depend'] is not None:
                        version.hard_dependencies = config['depend']

                    # Soft Dependencies
                    if 'softdepend' in config and config['softdepend'] is not None:
                        version.soft_dependencies = config['softdepend']

                    # Commands
                    if 'commands' in config and config['commands'] is not None:
                        version.commands = config['commands']

                    # Permissions
                    if 'permissions' in config and config['permissions'] is not None:
                        version.permissions = config['permissions']

                    # Allow for the ability of the latest update to override the
                    # plugin name.  We still use the url slug canonically,
                    # however this may be cleaner ;).
                    if 'name' in config and config['name'] is not None and not self.ymlname:
                        self.ymlname = config['name']

                    # Allow for the ability of the latest update to override the
                    # plugin description.
                    if 'description' in config and config['description'] is not None and not self.ymldesc:
                        self.ymldesc = config['description']

                # Now to cleanup...
                jar.close()
                data.close()

            # Lastly we will now commit this new version to the database.
            s.add(version)
            s.commit()
            changes = 1
        return changes