import time
import yaml
import json
import re
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
    revex = re.compile(r'\d{1,3}\.{0,1}\d{0,3}\.{0,1}\d{0,3}')

    # This regex is used to parse out the plugin status.
    restage = re.compile(r'project-stage')


    def run(self, speedy=True):
        '''run speedy=True
        This function is the main function to launch the parser.  The speedy
        flag denoted whether the parser will run through the entire DBO database
        or will only check for those items it does not have in the database.
        '''
        self.complete = False
        self._server_mods(speedy)
        self.complete = True


    def _server_mods(self, speedy=True):
        '''_server_mods speedy=True
        This function is what will be parsing the plugin listing pages, looking
        for new plugins.
        '''
        # Here we set a few things up, we will get the current time in order
        # to set the duration for the meta object, instantiate a database
        # session, and lastly create a Meta object that we will be using.
        start = time.time()
        s = db.Session()
        self.meta = db.Meta()

        # Here we are querying the database for the repository row that we will
        # need throughout this process.  If one doesn't exist, then we will 
        # create it here.
        try:
            self.repo = s.query(db.Repo).filter_by(name='bukkit').one()
        except:
            self.repo = db.Repo('bukkit')
            s.add(self.repo)
            s.commit()

        # Here we will be pre-loading the current url (curl) variable and
        # setting running to True so that the while loop will just keep doing
        # it's thing.
        curl = self.base_uri
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
                    count += self._plugin(plugin)

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
            plugin = db.Plugin()
            s.add(plugin)
            log.debug('PARENT: Adding plugin %s in bukkit repository' % name)
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
                author = s.query(db.Author).filter_by(name=name).one()
            except:
                author = db.Author(author_name)
                s.add(author)
                s.commit()

            if author not in plugin.authors:
                plugin.authors.add(author)

        # and for the next fun item, categories!  We will be performing the 
        categories = [a.text for a in page.findAll('a', {'class': 'category'})]
        for cat_name in categories:
            try:
                category = s.query(db.Category).filter_by(name=cat_name).one()
            except:
                category = db.Category(cat_name)
                s.add(category)
                s.commit()

            if category not in plugin.categories:
                plugin.categories.add(category)

        # Now for some easier stuff, we will be parsing through the status,
        # the plugin's full name, and the plugin description.
        plugin.status = page.find('span', {'class': self.restage}).text
        plugin.description = page.find('div', {'class': 'content-box-inner'}).text
        plugname = page.find('div', {'class': 'global-navigation'}).findNextSibling('h1').text

        # This is a bit of a hack to get around some issues that have cropped up
        # thanks to plugins using unicode characters that just arent handled in
        # json.  Once we have a determination of what we can do, we will
        # populate that into the plugin.
        try: 
            json.dumps(plugname)
        except: 
            plugname = ''
        plugin.plugname = plugname

        # Now we need to merge the changes made and commit them into the
        # database before we go much further.  We will also close out the
        # session at this point because there will be no further changes to the
        # plugin object at this point.
        plugin = s.merge(plugin)
        s.commit()
        s.close()

        # Next we need to start working our way through the various versions.
        # This will be handled very much in the same way as how we were handling
        # plugins, by simply looking for the version slug and handing this
        # information off to a seperate function designed to better break down
        # the data.

        # Here we start out (just like before) by pre-loading the vurl variable
        # and setting the running flag to true.  We will also keep track of the
        # number of changes in order to speed things up a bit.
        vurl = '%s/files/' % dbo_link
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

            for row in rows:
                vlink = row.findNext('td', {'class': 'col-file'}).findNext('a').get('href')
                slug = self.vrex.findall(vlink)
                changes += self._version(plugin.id, slug)

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

        # Lastly, we will return the number of changes that we made.
        return count

