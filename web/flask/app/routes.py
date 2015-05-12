# -*- coding : utf-8 -*-                                                                               
from flask import Flask, request, render_template, jsonify, redirect, url_for
from werkzeug import secure_filename
from app import app
from app import db, models
from app import pisi

ALLOWED_EXTENSIONS = set(['pisi'])

def allowed_file( filename ):
  return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

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

if __name__ == '__main__':
  app.run(debug=True)



"""



import os
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename
 
UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['txt'])
 
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
 
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index'))
    return ""
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    <p>%s</p>
    "" % "<br>".join(os.listdir(app.config['UPLOAD_FOLDER'],))
"""
