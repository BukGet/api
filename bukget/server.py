import cmd
import logging
import config
import repository
from sqlalchemy.orm             import sessionmaker
from sqlalchemy                 import create_engine

class Commands(cmd.Cmd):
  intro   = motd
  prompt  = 'bukget[SERVER]>'
  repos   = None
  session = None
  engine  = None
  
  def __init__(self):
    cmd.Cmd.__init__(self):
    sql_string    = config.get('Database', 'connection_string')
    self.engine   = create_engine(sql_string)
    self.maker    = sessionmaker(bind=engine)
    self.session  = self.maker()
    self.repos    = self.session.query(repository.PackageRepository)
  
  def do_generate_repo(self):
    data  = ''
    for repo in self.repos:
      if repo.activated:
        if repo.update():
          data += '%s\n' % repo.json
          logging.log('INFO: %s added to canonical repository.' % repo.plugin)
        else:
          logging.log('INFO: %s failed to add.' % repo.plugin)
    
    repofile  = config.get('Paths', 'repository')
    repofile.write(data)
    repofile.close()
  
  def do_activations(self):
    for repo in self.repos:
      if not repo.activated:
        if repo.hash is '':
          repo.generate_activation_code()
          self.session.merge(repo)
          