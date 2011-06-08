#!/usr/bin/env python
# encoding: utf-8
"""
conv_json.py

Created by Steven McGrath on 2011-06-08.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import getopt
import json


help_message = '''
Converts old JSON format to the new one.  You may want to move some things
around after the conversion is complete.

 -o / --old [FILENAME]
 -n / --new [FILENAME]
'''


class Usage(Exception):
  def __init__(self, msg):
    self.msg = msg


def main(argv=None):
  if argv is None:
    argv = sys.argv
  try:
    try:
      opts, args = getopt.getopt(argv[1:], "o:n:h", ["help", "old=", "new="])
    except getopt.error, msg:
      raise Usage(msg)
  
    # option processing
    for option, value in opts:
      if option in ("-h", "--help"):
        raise Usage(help_message)
      if option in ("-o", "--old"):
        old_file = value
      if option in ("-n", "--new"):
        new_file = value
  
  except Usage, err:
    print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
    print >> sys.stderr, "\t for help use --help"
    return 2
  
  old = json.loads(open(old_file, 'r').read())
  
  new = {
   'name': old['name'],
   'authors': [old['author'],],
   'maintainer': old['author'],
   'description': old['description'],
   'website': old['website'],
   'categories': old['categories'],
   'versions': [],
  }

  for version in old['versions']:
    new['versions'].append({
      'version': version['version'],
      'required_dependencies': old['required_dependencies'],
      'optional_dependencies': old['optional_dependencies'],
      'conflicts': [],
      'location': version['location'],
      'checksum': version['checksum'],
      'branch': version['branch'],
      'engines': [{
        'engine': 'craftbukkit',
        'build_min': version['bukkit_min'],
        'build_max': version['bukkit_max'],
      }],
    })
  
  open(new_file, 'w').write(json.dumps(new, indent=4))


if __name__ == "__main__":
  sys.exit(main())