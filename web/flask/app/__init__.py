from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from lxml import objectify


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
pisi = objectify.fromstring(open("pisi-index.xml").read())

from app import routes
