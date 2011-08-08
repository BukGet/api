# encoding: utf-8
"""
burt.py

Created by Steven McGrath on 2011-07-07.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import getopt
import yaml
import json
import zipfile
import os
import cmd
import hashlib

__version__ = '0.0.a3'
__author__ = 'Steven McGrath, and Nijikokun'

_motd = '''BuRT (BukGet Repository Tool) Version %s
Written By: %s

Please keep in mind that this tool is still in active development and may
change at any time.  We do not promise that this application will always
work so we recommend that you backup the files that you plan on using this
tool with before running burt.
''' % (__version__, __author__)

def listr(items, delim):
  dset = items.split(delim)
  vals = []
  if items in [None, 'None', '""', '']:
    return []
  else:
    for i in dset:
      vals.append(i.strip())
    return vals

class BuRT(cmd.Cmd):
  prompt = 'BuRT> '
  json_file = 'package.json'
  plugin_file = None
  yml_data = {}
  json_data = {'versions': []}
  
  def __init__(self, json_file=None, plugin_file=None):
    cmd.Cmd.__init__(self)
    if json_file is not None:
      self.do_load('json %s' % json_file)
    if plugin_file is not None:
      self.do_load('plugin %s' % plugin_file)
  
  def _parse_fields(self, fields, opts, data, accept_defaults=False):
    tmp = {}
    # Here we define the loop and the options that will be iterated through
    for item in fields:
      flag = False
      # First we will check to see if there is a yaml definition for this
      # item and will start with that.
      if item['yaml'] is not None:
        if item['yaml'] in self.yml_data:
          if item['type'] == 'string':
            tmp[item['json']] = str(self.yml_data[item['yaml']])
            flag = True
          elif item['type'] == 'int':
            tmp[item['json']] = int(self.yml_data[item['yaml']])
            flag = True
          else:
            tmp[item['json']] = self.yml_data[item['yaml']]
            flag = True
          print 'Set %s to %s from YAML' % (item['json'], tmp[item['json']])
      
      # Next we will check to see if there is any existing data in the json
      # data we have.  This will override the yaml data as it's historical
      # and considered more "trusted".  If the data in the historical json
      # is a default value, we will ignore it however.  This is not a flagged
      # event.
      if item['json'] in data:
        if data[item['json']] not in ['', [], 0, 9999]:
          tmp[item['json']] = data[item['json']]
      
      # Next we will parse through the options that have been specified and
      # will override anything that has already been set with the option that
      # was set.
      for opt, val in opts:
        if opt in item['options']:
          flag = True
          if item['type'] == 'list':
            tmp[item['json']] = listr(val, ',')
          elif item['type'] == 'int':
            tmp[item['json']] = int(val)
          else:
            tmp[item['json']] = str(val)
          print 'Set %s to %s from option' % (item['json'], tmp[item['json']])
      
      # Lastly, if no flags were set, as the user to input the information
      # manually.  Also show them what we currently have.
      if not flag:
        if item['json'] in tmp:
          hist_val = tmp[item['json']]
        else:
          hist_val = None
        if hist_val is not None and accept_defaults:
          print 'Using default %s: %s' % (item['json'], tmp[item['json']])
        else:
          raw = raw_input('%s [%s]: ' % (item['input'], hist_val))       
          if raw == '' and hist_val is not None:
            tmp[item['json']] = hist_val
          elif item['type'] == 'list':
            tmp[item['json']] = listr(raw, ',')
          elif item['type'] == 'int':
            tmp[item['json']] = int(raw)
          else:
            tmp[item['json']] = raw
    return tmp
  
  def do_load(self, s):
    '''load [FILETYPE] [FILENAME]
    '''
    if len(s.split()) != 2:
      print 'Invalid number of arguments'
      return
    ftype, fname = s.split()
    if ftype not in ['json', 'plugin']:
      print 'Invalid filetype.  Please specify json or plugin.'
      return
    if ftype == 'json':
      self.json_file = fname
      if not os.path.exists(fname):
        print 'Filename does not exist!'
        return
      try:
        jdata = json.loads(open(fname).read())
      except:
        print 'Could not read file or file is not properly formatted json.'
      else:
        self.do_validate(data=jdata):
        self.json_data = jdata
        print 'Json dictionary loaded.'
    if ftype == 'plugin':
      if not os.path.exists(fname):
        print 'Filename does not exist!'
        return
      try:
        zfile = zipfile.ZipFile(fname)
      except:
        print 'Not a Jar file.'
        return
      try:
        pyml = zfile.open('plugin.yml')
      except:
        print 'No plugin.yml exists in the plugin.'
        return
      try:
        self.yml_data = yaml.load(pyml.read())
      except:
        print 'YAML file in plugin is not valid.'
        return
      md5sum = hashlib.md5()
      md5sum.update(open(fname).read())
      self.yml_data['checksum'] = md5sum.hexdigest()
      self.plugin_file = fname
  
  def do_set(self, s):
    '''set [option] [value]
    Sets and of the following options
    json  [filename]
    '''
    if len(s.split()) >= 2:
      opt = s.split()[0]
      val = ' '.join(s.split()[1:])
      if opt == 'json':
        self.json_file = val
  
  def do_save(self, s=None):
    '''save
    Saves the current json data to disk.
    '''
    jfile = open(self.json_file, 'w')
    jfile.write(json.dumps(self.json_data, sort_keys=True, indent=4))
    jfile.close()
  
  def do_exit(self, s):
    '''exit
    Exits interactive mode.
    '''
    return True
  
  def do_show(self, s):
    '''show
    Will generate the json based on what is currently in memory and will
    display it for the user to see.
    '''
    print json.dumps(self.json_data, sort_keys=True, indent=4)
  
  def do_global(self, s):
    '''global [OPTIONS]
    Handles adding and updating data part of the global section of the json
    dictionary.

    OPTIONS:

    -n (--name)     [PLUGINNAME]    Name of the plugin.  Can't contain spaces.

    -a (--authors)  [COMMA,SEP,LST] A Comma-separated list of the names of the
                                    plugin authors.

    -m (--maintainer) [MAINTAINER]  The plugin maintainer.  This persion
                                    typically matches the originating poster
                                    for the plugin thread on the bukkit
                                    forums.

    -w (--website)  [URL]           URL pointing to the plugin's webpage.
    
    -d (--description) [DESCRIPTION]   

    -c (--categories) [LIST,OF,CATS]Comma-separated list of categories that
                                    the plugin is a member of.  Please do not
                                    use complex categories (i.e. ADMN/FUN) but
                                    instead seperate each category into the
                                    list.  This helps to prevent category
                                    cruft in the repository.

    -s (--save)                     Will force save the file after the data
                                    has been parsed.
    
    -y (--yes)                      If a value has already been set,
                                    automatically accept that value and do not
                                    prompt.
    '''
    opts, args = getopt.getopt(s.split(), 'a:n:m:w:c:d:sy',
                               ['name=', 'authors=', 'maintainer=', 
                                'website=', 'categories=', 'description=', 
                                'yes'])
    save = False
    defaults = False
    for opt, val in opts:
      if opt in ('-s', '--save'):
        save = True
      if opt in ('-y', '--yes'):
        defaults = True
    
    # Here we define the loop and the options that will be iterated through
    items = [{
              'json': 'name',
              'options': ('-n, --name'),
              'type': 'string',
              'yaml': 'name',
              'input': 'Enter Plugin Name (no spaces)'
             },{
              'json': 'maintainer',
              'options': ('-m', '--maintainer'),
              'type': 'string',
              'yaml': 'maintainer',
              'input': 'Enter Plugin Maintainer',
             },{
              'json': 'authors',
              'options': ('-a', '--authors'),
              'type': 'list',
              'yaml': 'authors',
              'input': 'Enter Authors (Comma-Separated)',
             },{
              'json': 'website',
              'options': ('-w', '--website'),
              'type': 'string',
              'yaml': 'website',
              'input': 'Enter Website Address',
             },{
              'json': 'categories',
              'options': ('-c', '--categories'),
              'type': 'list',
              'yaml': 'categories',
              'input': 'Enter Categories (Comma-Separated)'
             },{
              'json': 'description',
              'options': ('-d', '--description'),
              'type': 'string',
              'yaml': 'description',
              'input': 'Enter Description'
             }]
    tmp = self._parse_fields(items, opts, self.json_data, defaults)
    for key in tmp:
      self.json_data[key] = tmp[key]
    
    if save:
      self.do_save()
  
  def do_version(self, s):
    '''version [OPTIONS]
    Handles adding, updating, and deleting versions from the json dictionary.
    
    OPTIONS:
    
    -v (--version)  [VERSION]       The version number for this specific
                                    version.
                                    
    -l (--location) [URL]           URL pointing to the plugin package version
    
    -c (--checksum) [CHECKSUM]      Checksum of the plugin package version
    
    -b (--branch)   [BRANCH]        Branch tree of the plugin package version.
                                    This must be either dev, test, or stable.
                                    
    -W (--warn)     [WARNING]       This warning will be displayed to the user
                                    when they try to update or install the
                                    package.  Please note that this will stop
                                    installation until the user accepts.
                                    
    -N (--notify)   [NOTIFICATION]  Notification message after the install has
                                    completed.
                                    
    -C (--conflict) [LIST,OF,PLUGS] Comma-separated list of plugins that will
                                    conflict with the plugin.
                                    
    -R (--required) [LIST,OF,PLUGS] Comma-separated list of plugins that are
                                    required in order for this plugin to work.
                                    
    -O (--optional) [LIST,OF,PLUGS] Comma-separated list of plugins that the
                                    plugin can optionally hook into.
                                    
    -e (--engine)   [NAME:MIN:MAX]  Specifies what server the plugin will work
                                    with and what the minimum and maximum
                                    build numbers for that server that the
                                    plugin will work with.  This option can
                                    be specified multiple times for multiple
                                    engines.
                                    
    -s (--save)                     Will force save the file after the data
                                    has been parsed.
    
    -y (--yes)                      If a value has already been set,
                                    automatically accept that value and do not
                                    prompt.
    '''
    opts, args = getopt.getopt(s.split(), 'v:l:c:b:W:N:C:R:O:e:sy',
                               ['version=', 'location=', 'checksum=', 
                                'branch=', 'warn=', 'notify=', 'conflict=',
                                'required=', 'optional=', 'engine=', 'save',
                                'yes'])
    save = False
    tmp = {}
    ver = None
    defaults = False
    engines = []
    for opt, val in opts:
      if opt in ('-s', '--save'):
        save = True
      if opt in ('-y', '--yes'):
        defaults = True
      if opt in ('-v', '--version'):
        ver = val
      if opt in ('-e', '--engine'):
        engine_name, build_min, build_max = val.split(':')
        engines.append({
          'engine': engine_name,
          'build_min': int(build_min),
          'build_max': int(build_max),
        })
    
    # If there was no version flag set, then check the plugin for the version
    # information and pull that.
    if ver == None and 'version' in self.yml_data:
      ver = str(self.yml_data['version'])
    
    # Now we should have a version from something, if not then throw an error,
    # otherwise we need to pull the version information from the json data
    # to send that onto the parser.
    if ver is not None:
      vdata = {}
      for version in self.json_data['versions']:
        if version['version'] == ver:
          vdata = version
          vindex = self.json_data['versions'].index(vdata)
          if len(engines) == 0 and 'engines' in vdata:
            engines = vdata['engines']
      if vdata == {}:
        self.json_data['versions'].append(vdata)
        vindex = -1
    else:
      print 'No version specified.  Please either load a plugin file\n' +\
            ' or set a version via the version flag.'
      return
    
    # New we need to setup the item dictionary list for the parser.
    items = [{
              'json': 'version',
              'options': ('-v', '--version'),
              'type': 'string',
              'yaml': 'version',
              'input': 'Enter Version Number',
             },{
              'json': 'location',
              'options': ('-l', '--location'),
              'type': 'string',
              'yaml': 'location',
              'input': 'Enter Plugin File URL',
             },{
              'json': 'checksum',
              'options': ('-c', '--checksum'),
              'type': 'string',
              'yaml': 'checksum',
              'input': 'Enter Plugin MD5 Checksum',
             },{
              'json': 'branch',
              'options': ('-b', '--branch'),
              'type': 'string',
              'yaml': 'branch',
              'input': 'Enter branch (dev, test, or stable)',
             },{
              'json': 'conflicts',
              'options': ('-C', '--conflict'),
              'type': 'list',
              'yaml': 'conflicts',
              'input': 'Enter Conflictions (Comma-Separated)',
             },{
              'json': 'required_dependencies',
              'options': ('-R', '--required'),
              'type': 'list',
              'yaml': 'depend',
              'input': 'Enter Hard Dependencies (Comma-Separated)',
             },{
              'json': 'optional_dependencies',
              'options': ('-O', '--optional'),
              'type': 'list',
              'yaml': 'softdepend',
              'input': 'Enter Soft Dependencies (Comma-Separated)',
             }]
    tmp = self._parse_fields(items, opts, vdata, defaults)
    
    if len(engines) < 1:
      build_min = None
      build_max = None
      
      while build_min is None:
        try:
          build_min = int(raw_input('Enter Minimum Craftbukkit Build: '))
        except:
          print 'Minimum build must be an integer, please try again.'
      
      while build_max is None:
        try:
          build_max = int(raw_input('Enter Maximum Craftbukkit Build: '))
        except:
          print 'Maximum build must be an integer, please try again.'
        if build_max < build_min:
          print 'Maximum build must not be less than that the Minimum Build.'
          build_max = None
      
      engines.append({
        'engine': 'craftbukkit',
        'build_min': build_min,
        'build_max': build_max
      })
    tmp['engines'] = engines
    
    
    for key in tmp:
      self.json_data['versions'][vindex][key] = tmp[key]
    
    if save:
      self.do_save()
  
  def do_validate(self, s=None, data=None):
    if data is not None:
      d = data
    else:
      d = self.json_data
    
    flag = False
    if 'name' not in d: 
      print 'Missing name'
      flag = True
    else:
      if not isinstance(d['name'], unicode): 
        print 'Name is not encased in quotes...'
        flag = True
    if 'authors' not in d: 
      print 'missing authors'
      flag = True
    else:
      if not isinstance(d['authors'], list): 
        print 'Authors is not in list form.'
        flag = True
    if 'maintainer' not in d: 
      print 'Missing maintainer.'
      flag = True
    else:
      if not isinstance(d['maintainer'], unicode): 
        print 'Maintainer not encased in quotes...'
        flag = True
    if 'description' not in d: 
      print 'Missing Description.'
      flag = True
    else:
      if not isinstance(d['description'], unicode): 
        print 'Description not encased in quotes...'
        flag = True
    if 'website' not in d: 
      print 'Missing website.'
      flag = True
    else:
      if not isinstance(d['website'], unicode): 
        print 'Website not encased in quotes...'
        flag = True
    if 'categories' not in d: 
      print 'Missing categories.'
      flag = True
    else:
      if not isinstance(d['categories'], list): 
        print 'Categories are not in array form.'
        flag = True
    if 'versions' not in d: 
      print 'Missing versions.'
      flag = True
    else:
      if not isinstance(d['versions'], list): 
        print 'Versions is not in array form.'
        flag = True
      else:
        for v in d['versions']:
          if 'version' not in v: 
            print 'Missing version value on a version object'
            vstr = 'in unknown version'
            flag = True
          else:
            vstr = 'in %s' % v['version']
          if not isinstance(v['version'], unicode): 
            print 'Version not unicode %s' % vstr
            flag = True
          if 'required_dependencies' not in v: 
            print 'Missing required_dependencies value %s' % vstr
            flag = True
          else:
            if not isinstance(v['required_dependencies'], list): 
              print 'required_dependencies is not a list %s' % vstr
              flag = True
          if 'optional_dependencies' not in v: 
            print 'Missing optional_dependencies value %s' % vstr
            flag = True
          else:
            if not isinstance(v['optional_dependencies'], list): 
              print 'optional_dependencies is not a list %s' % vstr
              flag = True
          if 'conflicts' not in v: 
            print 'Missing conflicts value %s' % vstr
            flag = True
          else:
            if not isinstance(v['conflicts'], list): 
              print 'Conflicts are not in list form %s' % vstr
              flag = True
          if 'location' not in v: 
            print 'Missing location value %s' % vstr
            flag = True
          else:
            if not isinstance(v['location'], unicode): 
              print 'Location not encased in quotes %s' % vstr
              flag = True
          if 'checksum' not in v: 
            print 'Missing checksum value %s' % vstr
            flag = True
          else:
            if not isinstance(v['checksum'], unicode): 
              print 'Checksum not encased in quotes %s' % vstr
              flag = True
          if 'branch' not in v: 
            print 'Missing branch value %s' % vstr
            flag = True
          else:
            if not isinstance(v['branch'], unicode): 
              print 'Branch not encased in quotes %s' % vstr
              flag = True
            if v['branch'] not in ['stable','test','dev']: 
              print 'branch must be [stable, dev, or test] %s' % vstr
              flag = True
          if 'engines' not in v:
            print 'Missing engine value %s' % vstr
            flag = True
          else:
            if not isinstance(v['engines'], list):
              print 'engines is not a list %s' % vstr
              flag = True
            else:
              for e in v['engines']:
                if 'engine' not in e: 
                  print 'Missing engine key'
                  estr = 'on unknown engine %s' % vstr
                  flag = True
                else:
                  estr = 'on %s %s' % (e['engine'], vstr)
                  if not isinstance(e['engine'], unicode): 
                    print 'Engine not encased in quotes %s' % estr
                    flag = True
                if 'build_min' not in e: 
                  print 'Missing build_min key %s' % estr
                  flag = True
                else:
                  if not isinstance(e['build_min'], int): 
                    print 'build_min not integer %s' % estr
                    flag = True
                if 'build_max' not in e: 
                  print 'Missing build_max key %s' % estr
                  flag = True
                else:
                  if not isinstance(e['build_max'], int): 
                    print 'build_max not integer %s' % estr
                    flag = True
                  else:
                    if not e['build_min'] <= e['build_max']: 
                      print 'build_min is not less than build_max %s' % estr
                      flag = True
    if flag:
      print 'ERROR: There are errors in your json dictionary.'
    return not flag
    
    

if __name__ == '__main__':
  if len(sys.argv) == 1:
    BuRT().cmdloop(_motd)
  elif len(sys.argv) == 2:
    BuRT(json_file=sys.argv[1]).cmdloop(_motd)
  elif len(sys.argv) == 3:
    BuRT(json_file=sys.argv[1], plugin_file=sys.argv[2]).cmdloop(_motd)
  else:
    BuRT(json_file=sys.argv[1], plugin_file=sys.argv[2]).onecmd(\
                                                      ' '.join(sys.argv[3:]))