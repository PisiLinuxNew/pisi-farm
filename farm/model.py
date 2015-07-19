# -*- coding : utf-8 -*-
__author__ = 'ilker'

from sqlalchemy import Column, ForeignKey, Boolean, Integer, String, DateTime
from sqlalchemy.orm import relationship
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

"""
REPOS = {'0':{'repo' : 'pisilinux/core',
          'branch' : 'master',
          'dockerimage' : 'ertugerata/pisi-chroot-farm',
          'repo_dir' : '/var/www/html/pisilinux-core',
          'upload' : "/var/www/html/pisi-upload/",
          'repo_url' : 'https://github.com/pisilinux/core/raw/master/pisi-index.xml.xz' }}
"""

class Repo(Base):
    __tablename__ = "repo"
    id = Column(Integer, primary_key=True)
    repo = Column(String(100))
    repourl = Column(String(200))
    branch = Column(String(100))
    dockerimage = Column(String(150))
    repodir = Column(String(200))
    enable = Column(Boolean)

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
    paket = relationship('Paket')
    commit_id = Column(String(40))
    commit_url = Column(String(100))
    durum = Column(Integer, default = 0)
    repository = Column(String(150))
    branch = Column(String(100))
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
    gonullu = relationship('Gonullu')
    basari = Column(Boolean)
    kuyruk_id = Column(Integer, ForeignKey("kuyruk.id"))
    kuyruk = relationship('Kuyruk')

#engine = create_engine('sqlite:////tmp/farm.db')
engine = create_engine('postgresql://postgres:system@localhost/pisi')
session = sessionmaker()
session.configure(bind=engine)
ses = session()

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    import sys, codecs
    if len(sys.argv) > 1:
        lines = codecs.open(sys.argv[1],encoding="utf-8").readlines()
        for l in lines:
            print l[:43].strip(),l[43:].strip()
            p = Paket(adi=l[:43].strip(), aciklama = l[43:].strip() )
            ses.add(p)
            ses.commit()

