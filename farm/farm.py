from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, BooleanField
from model import *
from github import Push
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.sql import label
import json
from sqlalchemy.orm import class_mapper
from repo import repos, REPOBASE

def serialize(model):
    """Transforms a model into a dictionary which can be dumped to JSON."""
    # first we get the names of all the columns on your model
    columns = [c.key for c in class_mapper(model.__class__).columns]
    # then we return their values in a dict
    return dict((c, getattr(model, c)) for c in columns)




app = Flask(__name__)
app.config.from_object('config')


class RepoForm(Form):
    repo = StringField('repo')
    branch = StringField('branch')
    repourl = StringField('repourl')
    dockerimage = StringField('dockerimage')
    repodir = StringField('repodir')
    enable = BooleanField('enable')
    submit = SubmitField('Kaydet')


def repostat(repoid = -1):
    if repoid == -1:
        return ses.query(Kuyruk.repository, Kuyruk.branch, Kuyruk.durum, label('sayi', func.count(Kuyruk.id))).group_by(Kuyruk.repository, Kuyruk.branch, Kuyruk.durum).all()
    else:
        cevap = ses.query(Repo.repo, Repo.branch).filter_by(id=repoid).one()
        c2 = ses.query(Kuyruk.repository, Kuyruk.branch, Kuyruk.durum,
                         label('sayi', func.count(Kuyruk.id))).filter_by(repository=cevap.repo , branch=cevap.branch).group_by(
            Kuyruk.repository, Kuyruk.branch, Kuyruk.durum).all()
        return c2


def check_branch_db(r, b):
    return (ses.query(Repo).filter_by(enable=True,repo=r, branch=b).count() == 1)

def check_branch(r, b):
    for k, v in app.config["REPOS"].items():
        if ((v['repo'] == r) and (v['branch'] == b)):
            return True
    return False


def commitCheck(pkgid, commitid):
    return  ses.query(Kuyruk).filter_by(paket_id=pkgid, commit_id=commitid).count()


def paketID(pname):
    id = ses.query(Paket).filter_by(adi=pname).first().id
    return id



@app.route('/packages')
#@app.route('/packages/<int:page>')
def packages():
    pkglist = ses.query(Paket).all()
    return render_template("pkg.html", pkgs = pkglist)


@app.route('/about')
def about():
    return render_template('home.html')


@app.route('/sources')
def sources():
    return render_template('home.html')


@app.route('/compiling')
def compiling():
    return render_template('home.html')


@app.route('/queue')
def queue():
    vals = ses.query(Kuyruk).filter(Kuyruk.durum < 1000).join(Paket).order_by(Kuyruk.tarih.asc()).all()
    return render_template('queue.html', packages = vals)


@app.route('/')
@app.route('/repo/<int:id>')
@app.route('/repo/<int:id>/<pkgname>')
def home(id = -1, pkgname = ""):
    stat = repostat(id)
    if id > -1:
        repo = repos[id]
        if pkgname == "":
            return render_template('repodetail.html', repo = [repo], stat = stat, pkgs = sorted(repo.paketler.keys()))
        else:
            pkg = repos[id].pkginfo(pkgname)
            return render_template('pkgdetail.html', repo = [repo], stat = stat, pkg = pkg)
    else:
        repo = ses.query(Repo).all()
        return render_template('home.html', repo = repo, stat = stat)


@app.route('/admin')
def admin():
    repolar = ses.query(Repo).all()
    return render_template("admin.html", repo = repolar)


@app.route('/admin/addrepo', methods=['GET', 'POST'])
def adminAddRepo():
    form = RepoForm()
    if request.method == 'GET':
        return render_template("adminAddRepo.html", form=form)
    elif request.method == 'POST':
        sayi = ses.query(Repo).filter_by(repo=form.repo.data, branch=form.branch.data).count()
        if sayi == 0:
            r = Repo(repo=form.repo.data, repourl=form.repourl.data,
                     branch=form.branch.data, dockerimage=form.dockerimage.data,
                     repodir=form.repodir.data, enable=form.enable.data)
            ses.add(r)
            ses.commit()
            return "kaydedildi"
        else:
            return "zaten varmis %d" % sayi


@app.route('/requestPkg/<string:email>')
def requestPkg(email):
    try:
        gonullu_id = ses.query(Gonullu).filter(Gonullu.email == email).one().id
    except:
        return "ilkermanap@gmail.com adresine mektup atarak gonullu olmak istediginizi belirtin"
    kuyruk = ses.query(Kuyruk).filter(Kuyruk.durum < 100).order_by(Kuyruk.id.asc()).first()
    print ">>>> ", kuyruk
    print kuyruk.id
    k = ses.query(Kuyruk)
    k = k.filter(Kuyruk.id == kuyruk.id)
    kayit = k.one()
    kayit.durum = 100
    ses.flush()
    yeniGorev = Gorev(gonullu_id=gonullu_id, kuyruk_id = kuyruk.id)
    ses.add(yeniGorev)
    ses.flush()
    paketadi = ses.query(Paket).filter(Paket.id == kuyruk.paket_id).first().adi
    ses.commit()
    cevap = {'kuyruk_id': kuyruk.id, 'paket': paketadi, 'commit_id':kuyruk.commit_id, 'repo': kuyruk.repository, 'branch': kuyruk.branch }
    print ">>>>> ", cevap
    return jsonify(cevap)


@app.route('/parameter')
def parameters():
    return json.dumps([serialize(repo) for repo in ses.query(Repo).all()])

@app.route('/githubhook', methods = ["PUT", "POST"])
def githubhook():
    committarihi = datetime.strftime(datetime.now(),"%Y%m%d%H%M%S")
    f = open("/tmp/github-%s.txt" % committarihi, "w")
    f.write(request.data)
    f.close()
    gitcommit("github-%s.txt" % committarihi)


@app.route("/updaterunning/", methods = ['GET'])
def updaterunning():
    kid = int(request.args.get('id'))
    stat = int(request.args.get('state'))
    if stat == 0:
        basari = 999 # success
    else:
        basari = 101 # fail
    
    k = ses.query(Kuyruk)
    k = k.filter(Kuyruk.id == kid)
    kayit = k.first()
    kayit.durum = basari
    ses.flush()
    ses.commit()
    return "ok"



@app.route('/gitcommit/<string:fname>')
def gitcommit(fname):
    f = "/tmp/%s" % fname
    p = Push(f)
    d = p.db()
    bra = p.ref
    rep = p.data['repository']["full_name"].replace("https://github.com/", "")
    if check_branch_db(rep, bra) == True:
        tar = p.data['repository']['updated_at']
        tar = tar.replace("Z","").replace("T"," ")
        t = datetime.strptime(tar,"%Y-%m-%d %H:%M:%S")
        for _id, com in p.db().items():
            id = com['id']
            url = com['url']
            for pkg in com['modified']:
                pkgid = paketID(pkg)
                if commitCheck(pkgid, id) == 0:
                    print id
                    k = Kuyruk(tarih=t, paket_id=pkgid, commit_id=id, \
                                      commit_url=url, durum=0, repository=rep, \
                                      branch=bra)
                    ses.add(k)
                    ses.commit()
        return p.ref
    return p.ref


@app.route('/upload', methods = ['POST'])
def upload():
    import os
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            kuyruk_id = filename.split("-")[0]
            k = s.query(Kuyruk).filter(id == kuyruk_id).first()
            pa = s.query(Paket).filter(paket_id == k.paket_id).first().adi
            trh = datetime.strftime(datetime.now(),"%Y%m%d%H%M%S")
            if pa[:3] == "lib":
                # lib ile basliyorsa
                pre = pa[:4]
            else:
                pre = pa[0]
            pkgdir = "/%s/%s/%s-%s/" % (pre, pa, trh, k.commit_id)


            p = os.path.join(REPOBASE, k.repository, k.branch, pkgdir)   
            os.system("mkdir -p %s" % p)
            f = os.path.join(p, filename)
            file.save(f)
            hash = os.popen("sha1sum %s" % f, "r").readlines()[0].split()[0].strip()
            return hash 




if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
