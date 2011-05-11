#!/usr/bin/env python
# encoding: utf-8
"""
bukget_service.py

Created by Steven McGrath on 2011-05-04.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from subprocess                 import Popen, PIPE
from SimpleXMLRPCServer         import SimpleXMLRPCServer
from SimpleXMLRPCServer         import SimpleXMLRPCRequestHandler

class BukkitHandler(object):
  process           = None
  
  def start(self, mem_min=512, mem_max=1024):
    if not self.running():
      startup           = 'java -Xms%sm -Xmx%sm -jar craftbukkit.jar' %\
                            (mem_min, mem_max)
      self.process      = Popen(startup, 
                                  stdin=PIPE, 
                                  stdout=PIPE, 
                                  stderr=PIPE,
                                  shell=True)
      return True
  
  def communicate(self, cmd, lines=1):
    output  = []
    self.process.stderr.flush()
    self.process.stdin.write(cmd)
    for count in range(0,lines):
      output.append(self.process.stderr.readline())
    return ''.join(output)
  
  def players_online(self):
    pass
  
  def stop(self):
    self.process.communicate('stop\n')
  
  def running(self):
    if self.process is not None:
      if self.process.poll() is None:
        return True
    return False

class RequestHandler(SimpleXMLRPCRequestHandler):
  rpc_paths       = ('/RPC2',)

def daemonize():
  pidfile = 'bukkit_service.pid'
  # do the UNIX double-fork magic, see Stevens' "Advanced 
  # Programming in the UNIX Environment" for details (ISBN 0201563177)
  try: 
    pid = os.fork() 
    if pid > 0:
      # exit first parent
      sys.exit(0) 
  except OSError, e: 
    print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
    sys.exit(1)
  # decouple from parent environment
  os.chdir("/") 
  os.setsid() 
  os.umask(0) 
  # do second fork
  try: 
    pid = os.fork() 
    if pid > 0:
      # exit from second parent, print eventual PID before
      #print "Daemon PID %d" % pid
      open(pidfile, 'w').write('%d' % pid)
      sys.exit(0) 
  except OSError, e: 
    print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
    sys.exit(1) 
  # Redirect all console data to logfiles
  out_log = file('bukkit_service.log', 'a+')
  err_log = file('bukkit_service.err', 'a+', 0)
  dev_null = file('/dev/null', 'r')
  os.dup2(out_log.fileno(),   sys.stdout.fileno())

def main():
  address   = '127.0.0.1'
  port      = 9184
  server  = SimpleXMLRPCServer((address, port), 
                               requestHandler=RequestHandler,
                               logRequests=False)
  server.register_introspection_functions()
  server.register_instance(BukkitHandler())
  #daemonize()
  server.serve_forever()

if __name__ == '__main__':
  main()

