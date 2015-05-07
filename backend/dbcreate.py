# -*- coding : utf-8 -*-
from dbmodel import Base, engine

Base.metadata.create_all(engine)


from sqlalchemy import create_engine
from dbmodel import *
from sqlalchemy.orm import sessionmaker
session = sessionmaker()
session.configure(bind=engine)
liste = open("/root/paketler.txt","r").readlines()

s = session()
"""
for l in liste:
    l = l.replace("   - ","").strip()
    x = l.split()
    print x[0]
    p = Paket(adi = x[0], aciklama=l[l.rfind("   "):].strip())
    s.add(p)
    s.commit()

"""


sonuc = s.query(Paket).all()
for row in sonuc:
    print row.adi, row.aciklama

