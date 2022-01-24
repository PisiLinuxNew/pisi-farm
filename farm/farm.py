from flask import Flask, request, render_template, jsonify, redirect, url_for, session, escape
from flask_wtf import Form
from wtforms import StringField, SubmitField, BooleanField
from model import *
from github import Push
from datetime import datetime
from sqlalchemy import func, update
from sqlalchemy.sql import label
import json
from sqlalchemy.orm import class_mapper
from repo import repos, REPOBASE, pisi20repo, RepoBinary, RepoView
from werkzeug.utils import secure_filename
from indexer import  DockerIndexer
from performance import *
import traceback as tb
import os



perf = Performance()

ALLOWED_EXTENSIONS = set(['pisi','log','err', "html"])
blacklist = ["module-bbswitch", "module-broadcom-wl", "module-fglrx", "module-nvidia-current", "module-nvidia304", "module-nvidia340", "module-virtualbox", "module-virtualbox-guest", "ndiswrapper", "virtualbox", "klibc"]
def allowed_file( filename ):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def serialize(model):
    """Transforms a model into a dictionary which can be dumped to JSON."""
    # first we get the names of all the columns on your model
    columns = [c.key for c in class_mapper(model.__class__).columns]
    # then we return their values in a dict
    return dict((c, getattr(model, c)) for c in columns)



app = Flask(__name__)
app.config.from_object('config')
app.config["PROPAGATE_EXCEPTIONS"]  = True
app.secret_key = 'YSFeWkWKPdKhUHofYb6c'




if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
