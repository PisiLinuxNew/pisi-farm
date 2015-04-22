import os
import sys
from sqlalchemy import Column, ForeignKey, Boolean, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import sqlalchemy as sql
 
Base = declarative_base()
 
class Gonullu(Base):
    __tablename__ = "gonullu"
    id  = Column(Integer, primary_key=True)
    adi = Column(String(50), nullable=False)
    email = Column(String(100),nullable=False)

class Paket(Base):
    __tablename__ = "paket"
    id = Column(Integer, primary_key=True)
    adi = Column(String(50), nullable=False)
    aciklama = Column(String(200), nullable = False)

class Gorev(Base):
    __tablename__ = "gorev"
    id = Column(Integer, primary_key=True)
    tarih = Column(DateTime, default= sql.func.now())
    bitis = Column(DateTime)
    gonullu_id = Column(Integer, ForeignKey("gonullu.id"))
    gonullu = relationship(Gonullu)
    paket_id = Column(Integer, ForeignKey("paket.id"))
    paket = relationship(Paket)
    basari = Column(Boolean)


 
# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('postgresql://postgres:system@localhost/pisi')
 
