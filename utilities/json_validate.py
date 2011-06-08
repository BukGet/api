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
  
    # option processing
    for option, value in opts:
      if option in ("-h", "--help"):
        raise Usage(help_message)
      if option in ("-f", "--file"):
        json_file = value
  
  except Usage, err:
    print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
    print >> sys.stderr, "\t for help use --help"
    return 2
  
  d = json.loads(open(json_file, 'r').read())
  if 'name' not in d: return False
  if not isinstance(d['name'], unicode): return False
  if 'authors' not in d: return False
  if not isinstance(d['authors'], list): return False
  if 'maintainer' not in d: return False
  if not isinstance(d['maintainer'], unicode): return False
  if 'description' not in d: return False
  if not isinstance(d['description'], unicode): return False
  if 'website' not in d: return False
  if not isinstance(d['website'], unicode): return False
  if 'categories' not in d: return False
  if not isinstance(d['categories'], list): return False
  if 'versions' not in d: return False
  if not isinstance(d['versions'], list): return False
  for v in d['versions']:
    if 'version' not in v: return False
    if not isinstance(v['version'], unicode): return False
    if 'required_dependencies' not in v: return False
    if not isinstance(v['required_dependencies'], list): return False
    if 'optional_dependencies' not in v: return False
    if not isinstance(v['optional_dependencies'], list): return False
    if 'conflicts' not in v: return False
    if not isinstance(v['conflicts'], list): return False
    if 'location' not in v: return False
    if not isinstance(v['location'], unicode): return False
    if 'checksum' not in v: return False
    if not isinstance(v['checksum'], unicode): return False
    if 'branch' not in v: return False
    if not isinstance(v['branch'], unicode): return False
    if v['branch'] not in ['stable','test','dev']: return False
    for e in v['engines']:
      if 'engine' not in e: return False
      if not isinstance(e['engine'], unicode): return False
      if 'build_min' not in e: return False
      if not isinstance(e['build_min'], int): return False
      if 'build_max' not in e: return False
      if not isinstance(e['build_max'], int): return False
      if not e['build_min'] <= e['build_max']: return False
  print 'ok'
  
  


if __name__ == "__main__":
  sys.exit(main())