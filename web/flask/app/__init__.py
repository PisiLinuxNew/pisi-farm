from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from lxml import objectify


app = Flask(__name__)
app.config.from_object('config')
app.config['UPLOAD_FOLDER'] = '/var/www/pisi-upload'
db = SQLAlchemy(app)
pisi = objectify.fromstring(open("/root/pisi-index.xml").read())

from app import routes
