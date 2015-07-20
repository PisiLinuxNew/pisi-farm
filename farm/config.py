__author__ = 'ilker'


from lxml import objectify 
from model import *

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

REPOS = {'0':{'repo' : 'pisilinux/core',
          'branch' : 'master',
          'dockerimage' : 'ertugerata/pisi-chroot-farm',
          'repo_dir' : '/var/www/html/pisilinux-core',
          'upload' : "/var/www/html/pisi-upload/",
          'repo_url' : 'https://github.com/pisilinux/core/raw/master/pisi-index.xml.xz' }}

TEST="test"


repos = ses.query(Repo).all()

