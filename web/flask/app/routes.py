# -*- coding : utf-8 -*-                                                                               
from flask import Flask, render_template, jsonify
from app import app
from app import db, models
from app import pisi

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/queue')
def queue():
  pkgs=["acl","attr"]
  return render_template('queue.html', packages = pkgs)

@app.route('/requestPkg')
def requestPkg():
  pkg = "acl"
  return pkg

@app.route('/parameter')
def parameters():
  return jsonify({"docker-image": app.config["DOCKER_IMAGE_NAME"]})

@app.route('/packages')
@app.route('/packages/<int:page>')
def packages(page=1):
  pkglist = models.Paket.query.paginate(page, 30,False).items
  return render_template("pkg.html", pkgs = pkglist, page=page)

@app.route('/sourcepkg/<string:pkgname>')
def sourcepkg(pkgname):
  for p in pisi.iterchildren():
    if (p.tag == "SpecFile"):
      if p.Source.Name == pkgname:
        return render_template("sourcedetail.html", pkg = p)



@app.route('/source')
@app.route('/source/<string:packager>')
def sources(packager = "all"):
  temp = []
  for p in pisi.iterchildren():
    if (p.tag == "SpecFile"):
      temp.append((p.Source.Name, p))

  return render_template("sourcepkg.html", pkgs =sorted(temp), packager = packager)

if __name__ == '__main__':
  app.run(debug=True)



"""
# -*- coding : utf-8 -*-







liste = open("/root/paketler.txt","r").readlines()

s = session()
for l in liste:
    l = l.replace("   - ","").strip()
    x = l.split()
    print x[0]
    p = Paket(adi = x[0], aciklama=l[l.rfind("   "):].strip())
    s.add(p)
    s.commit()

sonuc = s.query(Paket).all()
for row in sonuc:
    print row.adi, row.aciklama
---------------------------------------





class Spec:
    def __init__(self, specObj):
        self.data = specObj

    def html(self):
        pass

def spec(name):

    for x in pisi.iterchildren():
        if x.tag == "SpecFile":
            if x.Source.Name == name:
                return x

"""
