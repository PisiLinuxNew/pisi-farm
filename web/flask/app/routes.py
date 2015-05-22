# -*- coding : utf-8 -*-                                                                               
from flask import Flask, request, render_template, jsonify, redirect, url_for
from werkzeug import secure_filename
from app import app
from app import db, models
from app import pisi
from app.models import *
from github import Push
from sqlalchemy.orm import sessionmaker

session = sessionmaker()
session.configure(bind = db.engine)
s = session()

ALLOWED_EXTENSIONS = set(['pisi','log','err'])



def allowed_file( filename ):
  return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def paketID(pname):
  id = Paket.query.filter_by(adi = pname).first().id
  return id

def commitCheck(pkgid, commitid):
  sonuc = Kuyruk.query.filter_by(paket_id=pkgid, commit_id=commitid).count()
  return sonuc

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/compiling')
def compiling():
  vals = s.query(Kuyruk).filter(Kuyruk.durum == 100).join(Paket).order_by(Kuyruk.tarih.asc()).all()
  return render_template('queue.html', packages = vals)

@app.route('/queue')
def queue():
  vals = s.query(Kuyruk).filter(Kuyruk.durum < 101).join(Paket).order_by(Kuyruk.tarih.asc()).all()
  return render_template('queue.html', packages = vals)

@app.route('/requestPkg/<string:email>')
def requestPkg(email):
  try:
    gonullu_id = s.query(Gonullu).filter(Gonullu.email == email).one().id
  except:
    return "ilkermanap@gmail.com adresine mektup atarak gonullu olmak istediginizi belirtin"
  kuyruk = s.query(Kuyruk).filter(Kuyruk.durum < 100).order_by(Kuyruk.id.asc()).first()
  k = s.query(Kuyruk)
  k = k.filter(Kuyruk.id == kuyruk.id)
  kayit = k.one()
  kayit.durum = 100
  s.flush()
  yeniGorev = Gorev(gonullu_id=gonullu_id, kuyruk_id = kuyruk.id)
  s.add(yeniGorev)
  s.flush()
  s.commit()
  return str(kuyruk.paket_id)

@app.route('/parameter')
def parameters():
  return jsonify(app.config["REPOS"])

@app.route('/packages')
@app.route('/packages/<int:page>')
def packages(page=1):
  pkglist = Paket.query.paginate(page, 30,False).items
  return render_template("pkg.html", pkgs = pkglist, page=page)

@app.route('/sourcepkg/<string:pkgname>')
def sourcepkg(pkgname):
  for p in pisi.iterchildren():
    if (p.tag == "SpecFile"):
      if p.Source.Name == pkgname:
        return render_template("sourcedetail.html", pkg = p)

@app.route('/upload', methods = ['POST'])
def upload():
  import os
  if request.method == 'POST':
    file = request.files['file']
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      f = os.path.join(app.config['UPLOAD_FOLDER'], filename)
      file.save(f)
      hash = os.popen("sha1sum %s" % f, "r").readlines()[0].split()[0].strip()
      return hash 


@app.route('/source')
@app.route('/source/<string:packager>')
def sources(packager = "all"):
  temp = []
  for p in pisi.iterchildren():
    if (p.tag == "SpecFile"):
      temp.append((p.Source.Name, p))

  return render_template("sourcepkg.html", pkgs =sorted(temp), packager = packager)

@app.route('/gitcommit/<string:fname>')
def gitcommit(fname):
  f = "/var/www/html/pisi-2.0/%s" % fname
  p = Push(f)
  d = p.db()
  bra = p.ref
  rep = p.data['repository']["full_name"]
  tar = p.data['repository']['updated_at']
  for _id, com in p.db().items():
    id = com['id']
    url = com['url']
    for pkg in com['modified']:
      pkgid = paketID(pkg)
      if commitCheck(pkgid, id) == 0:
        k = models.Kuyruk(tarih = tar, paket_id = pkgid, commit_id = id, \
                          commit_url = url, durum = 0, repository = rep, \
                          branch = bra)
        s.add(k)
        s.commit()
  return p.ref

if __name__ == '__main__':
  app.run(debug=True)
