from app import db
"""
from sqlalchemy import db.Column, ForeignKey, Boolean, Integer, db.String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import sqlalchemy as sql
"""

 
class Paket(db.Model):
    __tablename__ = "paket"
    id = db.Column(db.Integer, primary_key=True)
    adi = db.Column(db.String(100), nullable=False)
    aciklama = db.Column(db.String(200), nullable = False)

class Kuyruk(db.Model):
    __tablename__ = "kuyruk"
    id = db.Column(db.Integer, primary_key=True)
    tarih = db.Column(db.DateTime, default= db.func.now())
    paket_id = db.Column(db.Integer, db.ForeignKey("paket.id"))
    paket = db.relationship('Paket')
    commit_id = db.Column(db.String(40))
    commit_url = db.Column(db.String(100))
    durum = db.Column(db.Integer, default = 0)
    # 0 waiting 
    # 1 waiting partial
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
    tarih = db.Column(db.DateTime, default= db.func.now())
    bitis = db.Column(db.DateTime)
    gonullu_id = db.Column(db.Integer, db.ForeignKey("gonullu.id"))
    gonullu = db.relationship('Gonullu')
    basari = db.Column(db.Boolean)
    kuyruk_id = db.Column(db.Integer, db.ForeignKey("kuyruk.id"))
    kuyruk = db.relationship('Kuyruk')



 
# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
#engine = create_engine('postgresql://postgres:system@localhost/pisi')
 
