import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

OPENID_PROVIDERS = [
    {'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id'},
    {'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
    {'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
    {'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
    {'name': 'MyOpenID', 'url': 'https://www.myopenid.com'}]

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:system@localhost/pisi'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

GITHUB_CLIENT_ID = '65e59c67b178ea45257b'
GITHUB_CLIENT_SECRET = '6cc8509c765b5bf2ebb6203a03704f86a59ebf5a'
GITHUB_BASE_URL = 'https://api.github.com/'
GITHUB_AUTH_URL = 'https://github.com/login/oauth/'
