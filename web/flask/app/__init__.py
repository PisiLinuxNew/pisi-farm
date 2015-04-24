from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.github import GitHub

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
gituser = None
github = GitHub(app)

from app import routes
