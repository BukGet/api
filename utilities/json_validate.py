#!/usr/bin/env python
# encoding: utf-8
"""
json_validate.py

Created by Steven McGrath on 2011-06-08.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import getopt
import json


help_message = '''
Validates the json dictionary specified with current dictionary format.
  -f / --file [FILENAME]
'''


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "f:h", ["help", "file="])
        except getopt.error, msg:
            raise Usage(msg)

        # Process options
        for option, value in opts:
            if option in ("-h", "--help"):
                raise Usage(help_message)
            if option in ("-f", "--file"):
                json_file = value

    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2

    try:
        print 'Opening & Parsing %s' % json_file
        d = json.loads(open(json_file, 'r').read())
        if 'name' not in d: print 'Missing name'
        if not isinstance(d['name'], unicode): print 'Name is not encased in quotes...'
        if 'authors' not in d: print 'missing authors'
        if not isinstance(d['authors'], list): print 'Authors is not in list form.'
        if 'maintainer' not in d: print 'Missing maintainer.'
        if not isinstance(d['maintainer'], unicode): print 'Maintainer not encased in quotes...'
        if 'description' not in d: print 'Missing Description.'
        if not isinstance(d['description'], unicode): print 'Description not encased in quotes...'
        if 'website' not in d: print 'Missing website.'
        if not isinstance(d['website'], unicode): print 'Website not encased in quotes...'
        if 'categories' not in d: print 'Missing categories.'
        if not isinstance(d['categories'], list): print 'Categories are not in array form.'
        if 'versions' not in d: print 'Missing versions.'
        if not isinstance(d['versions'], list): print 'Versions is not in array form.'
        for v in d['versions']:
            if 'version' not in v: print 'Missing version value on a version object'
            if not isinstance(v['version'], unicode): print 'Version not unicode...'
            if 'required_dependencies' not in v: print 'Missing required_dependencies value in %s' % v['version']
            if not isinstance(v['required_dependencies'], list): print 'required_dependencies is not a list on %s' % v['version']
            if 'optional_dependencies' not in v: print 'Missing optional_dependencies value in %s' % v['version']
            if not isinstance(v['optional_dependencies'], list): print 'optional_dependencies is not a list on %s' % v['version']
            if 'conflicts' not in v: print 'Missing conflicts value in %s' % v['version']
            if not isinstance(v['conflicts'], list): print 'Conflicts are not in list form.'
            if 'location' not in v: print 'Missing location value in %s' % v['version']
            if not isinstance(v['location'], unicode): print 'Location not encased in quotes...'
            if 'checksum' not in v: print 'Missing checksum value in %s' % v['version']
            if not isinstance(v['checksum'], unicode): print 'Checksum not encased in quotes...'
            if 'branch' not in v: print 'Missing branch value in %s' % v['version']
            if not isinstance(v['branch'], unicode): print 'Branch not encased in quotes...'
            if v['branch'] not in ['stable','test','dev']: print 'incorrect branch value, must be [stable, dev, or test] in %s' % v['version']
            for e in v['engines']:
                if 'engine' not in e: print 'Missing engine key'
                if not isinstance(e['engine'], unicode): print 'Engine not encased in quotes...'
                if 'build_min' not in e: print 'Missing build_min key in %s' % v['version']
                if not isinstance(e['build_min'], int): print 'build_min not integer...'
                if 'build_max' not in e: print 'Missing build_max key in %s' % v['version']
                if not isinstance(e['build_max'], int): print 'build_max not integer..'
                if not e['build_min'] <= e['build_max']: print 'build_min is not less than build_max on %s' % v['version']
        print 'Finished parsing %s' % json_file
    except:
        print 'Could not read from %s' % json_file
        return False

if __name__ == "__main__":
    sys.exit(main())
