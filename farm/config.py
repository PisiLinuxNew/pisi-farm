__author__ = 'ilker'

import os
#from lxml import objectify 
#from model import *
#repos = ses.query(Repo).all()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = '971ae813bf3bf9664436e3590c338377ca576bfe2c24630f20c57fd91844a31ea637079c94144f22a40b392d16cc4ca0'
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://pisiuser:pisi2017@localhost/pisi'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMINS=["ilkermanap@gmail.com"]
    LANGUAGES = {"en": "English", "tr":"Turkish"}
    MAIL_SERVER="smtp.gmail.com"
    MAIL_PASSWORD='xxxxxxxxx'
    MAIL_PORT=465
    MAIL_USE_SSL=True
    MAIL_USE_TLS=False
    MAIL_USERNAME="ilkermanap@gmail.com"

    REPOS = {'0':{'repo' : 'pisilinux/core',
          'branch' : 'master',
          'dockerimage' : 'pisilinux/chroot',
          #'dockerimage' : 'safaariman/pisi-chroot',
          'repo_dir' : '/var/www/html/pisilinux-core',
          'upload' : "/var/www/html/pisi-upload",
          'repo_url' : 'https://github.com/pisilinux/core/raw/master/pisi-index.xml.xz' }}

    TEST="test"