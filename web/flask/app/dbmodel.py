import os
import sys
from sqlalchemy import Column, ForeignKey, Boolean, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import sqlalchemy as sql
 
Base = declarative_base()
 
class Paket(Base):
    __tablename__ = "paket"
    id = Column(Integer, primary_key=True)
    adi = Column(String(100), nullable=False)
    aciklama = Column(String(200), nullable = False)

class Kuyruk(Base):
    __tablename__ = "kuyruk"
    id = Column(Integer, primary_key=True)
    tarih = Column(DateTime, default= sql.func.now())
    paket_id = Column(Integer, ForeignKey("paket.id"))
    paket = relationship(Paket)
    commit_id = Column(String(40))
    commit_url = Column(String(100))
    durum = Column(Integer, default = 0)
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

class Gonullu(Base):
    __tablename__ = "gonullu"
    id  = Column(Integer, primary_key=True)
    adi = Column(String(50), nullable=False)
    email = Column(String(100),nullable=False)


class Gorev(Base):
    __tablename__ = "gorev"
    id = Column(Integer, primary_key=True)
    tarih = Column(DateTime, default= sql.func.now())
    bitis = Column(DateTime)
    gonullu_id = Column(Integer, ForeignKey("gonullu.id"))
    gonullu = relationship(Gonullu)
    basari = Column(Boolean)
    kuyruk_id = Column(Integer, ForeignKey("kuyruk.id"))
    relationship(Kuyruk)



 
# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('postgresql://postgres:system@localhost/pisi')
 
