from sqlalchemy import create_engine
engine = create_engine('postgresql://postgres:system@localhost/pisi')
from dbcreate import Paket, Gonullu, Gorev
from sqlalchemy.orm import sessionmaker
session = sessionmaker()
session.configure(bind=engine)
s = session()
p = Paket(adi="acl", aciklama="access control list")
s.add(p)
s.commit()
p = Paket(adi="libreoffice", aciklama= "Libreoffice ofis paketi")
s.add(p)
s.commit()
sonuc = s.query(Paket).all()
for row in sonuc:
    print row.adi, row.aciklama
