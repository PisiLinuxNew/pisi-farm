# -*- coding : utf-8 -*-
__author__ = 'ilker'

from app import db
from app import app
from app import login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from datetime import datetime
from time import time
import jwt

import sqlalchemy as sql
from sqlalchemy.orm import relationship


"""
from sqlalchemy import db.Column, ForeignKey, Boolean, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
"""


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    __tablename__ = "users" 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    admin = db.Column(db.Integer, default=0) # 0 not admin, 1 admin
    enabled = db.Column(db.Integer, default=1) # 0 not enabled, 1 enabled

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Repo(db.Model):
    __tablename__ = "repo"
    id = db.Column(db.Integer, primary_key=True)
    repo = db.Column(db.String(100))
    repourl = db.Column(db.String(200))
    branch = db.Column(db.String(100))
    dockerimage = db.Column(db.String(150))
    repodir = db.Column(db.String(200))
    enable = db.Column(db.Boolean)
    binrepo = db.Column(db.String(150))
    binrepopath = db.Column(db.String(150))

class Paket(db.Model):
    __tablename__ = "paket"
    id = db.Column(db.Integer, primary_key=True)
    adi = db.Column(db.String(100), nullable=False)
    aciklama = db.Column(db.String(200), nullable = False)

class Kuyruk(db.Model):
    __tablename__ = "kuyruk"
    id = db.Column(db.Integer, primary_key=True)
    tarih = db.Column(db.DateTime, default= sql.func.now())
    paket_id = db.Column(db.Integer, db.ForeignKey("paket.id"))
    paket = relationship('Paket')
    commit_id = db.Column(db.String(40))
    commit_url = db.Column(db.String(100))
    durum = db.Column(db.Integer, default = 0)
    repository = db.Column(db.String(150))
    branch = db.Column(db.String(100))
    # 0 waiting
    # 1 waiting partial
    # 2 waiting missing dep
    # 100 in progress
    # if durum < 100 then it can be served to volunteers
    # compile can be suspended on one volunteer and resumed
    # on another
    # suspended job will have a tar file named
    # package_name-commit_id.tar, this file will be sent by
    # the volunteer, with the suspended state of compilation
    # resume is done via docker load < package_name-commit_id.tar
    # then pisi bi --build --ignore-safety package-name

class Gonullu(db.Model):
    __tablename__ = "gonullu"
    id  = db.Column(db.Integer, primary_key=True)
    adi = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100),nullable=False)

class Gorev(db.Model):
    __tablename__ = "gorev"
    id = db.Column(db.Integer, primary_key=True)
    tarih = db.Column(db.DateTime, default= sql.func.now())
    bitis = db.Column(db.DateTime)
    gonullu_id = db.Column(db.Integer, db.ForeignKey("gonullu.id"))
    gonullu = relationship('Gonullu')
    basari = db.Column(db.Boolean)
    kuyruk_id = db.Column(db.Integer, db.ForeignKey("kuyruk.id"))
    kuyruk = relationship('Kuyruk')

#engine = create_engine('sqlite:////tmp/farm.db')
#engine = create_engine('postgresql://postgres:pisi2017@localhost/pisi')
#engine = create_engine('postgresql://pisiuser:pisi2017@localhost/pisi')

#session = sessionmaker()
#session.configure(bind=engine)
#ses = session()

"""
if __name__ == "__main__":
    Base.metadata.create_all(engine)
    import sys, codecs
    if len(sys.argv) > 1:
        lines = codecs.open(sys.argv[1],encoding="utf-8").readlines()
        for l in lines:
            print(l[:43].strip(),l[43:].strip())
            p = Paket(adi=l[:43].strip(), aciklama = l[43:].strip() )
            ses.add(p)
            ses.commit()
"""