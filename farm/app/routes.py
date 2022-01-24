from flask import render_template, flash, redirect, url_for, request, session
from app import app
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.forms import  ResetPasswordRequestForm, ResetPasswordForm
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User, Repo, Paket, Kuyruk, Gonullu, Gorev
from app import db
from app.email import send_password_reset_email
from flask_babel import lazy_gettext as _l
from datetime import datetime
from app.utils.decorators import admin_required
from sqlalchemy import func, update
from sqlalchemy.sql import label

ses = db.session()

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Ev')


@app.route('/language/<language>')
def set_language(language=None):
    session['language'] = language
    return redirect(request.referrer)


@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_l('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_l('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_l('Your changes have been saved.'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@app.route("/admin")
@login_required
@admin_required
def admin_page():
    users = User.query.all()
    return render_template("admin.html", users=users)


@app.route("/disable/<id>")
@login_required
@admin_required
def disable_user(id):
    user_to_disable = User.query.filter_by(id=id).first()
    user_to_disable.enabled = 0
    db.session.commit()
    return redirect(url_for('admin_page'))


@app.route("/revokeadmin/<id>")
@login_required
@admin_required
def revoke_admin(id):
    user_to_disable = User.query.filter_by(id=id).first()
    user_to_disable.admin = 0
    db.session.commit()
    return redirect(url_for('admin_page'))


@app.route("/grantadmin/<id>")
@login_required
@admin_required
def grant_admin(id):
    user_to_disable = User.query.filter_by(id=id).first()
    user_to_disable.admin = 1
    db.session.commit()

    return redirect(url_for('admin_page'))

@app.route("/deleteuser/<id>")
@login_required
@admin_required
def delete_user(id):
    User.query.filter_by(id=id).delete()
    db.session.commit()

    return redirect(url_for('admin_page'))


@app.route("/enable/<id>")
@login_required
@admin_required
def enable_user(id):
    user_to_enable = User.query.filter_by(id=id).first()
    user_to_enable.enabled = 1
    db.session.commit()

    return redirect(url_for('admin_page'))



@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_l('Check your email for the instructions to reset your password'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title=_l('Reset Password'), form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

#######################################################################
#
# farm routes starts from here
#
#######################################################################




class States:
    OK = 200
    MAILERR = 401
    NOPACKAGE = 402
    NODOCKERIMAGE = 403

states=States()

repos = ses.query(Repo).all()


def repostat(repoid = -1):
    if repoid == -1:
        try:
            return ses.query(Kuyruk.repository, Kuyruk.branch, Kuyruk.durum, label('sayi', func.count(Kuyruk.id))).group_by(Kuyruk.repository, Kuyruk.branch, Kuyruk.durum).all()
        except:
            pass
    else:
        cevap = ses.query(Repo.repo, Repo.branch).filter_by(id=repoid).one()
        c2 = ses.query(Kuyruk.repository, Kuyruk.branch, Kuyruk.durum,
                         label('sayi', func.count(Kuyruk.id))).filter_by(repository=cevap.repo , branch=cevap.branch).group_by(
            Kuyruk.repository, Kuyruk.branch, Kuyruk.durum).all()
        return c2


def check_branch_db(r, b):
    return (ses.query(Repo).filter_by(enable=True,repo=r, branch=b).count() == 1)

def check_branch(r, b):
    for k, v in repos.items():
        if ((v.repo == r) and (v.branch == b)):
            return True
    return False


def commitCheck(pkgid, commitid):
    return  ses.query(Kuyruk).filter_by(paket_id=pkgid, commit_id=commitid).count()


def paketID(pname):
    try:
        id = ses.query(Paket).filter_by(adi=pname).first().id
    except:
        id = None
    return id

def docker_image_name(r,b):
    for k, v in repos.items():
        if ((v.repo == r) and (v.branch == b)):
            return v.dockerimage
    return None

@app.route('/packages')
#@app.route('/packages/<int:page>')
def packages():
    pkglist = ses.query(Paket).all()
    return render_template("pkg.html", pkgs = pkglist)

@app.route('/binpackage/<string:name>')
def binpackage(name):
    for k,v in repos.items():
        if name in v.paketler:
            return  "%s True" % name
        else:
            return  "%s False" % name

@app.route('/about')
def about():
    return render_template('about.html')
    
@app.route("/findlistcore")
def findlistcore():
    #import os
    os.system("python findpackagescore.py")
    txtread = open('findcore.txt')
    data = txtread.read()
    return render_template("findlist.html", veri = data)

@app.route("/findlistmain")
def findlistmain():
    #import os
    os.system("python findpackagesmain.py")
    txtread = open('findmain.txt')
    data = txtread.read()
    return render_template("findlist.html", veri = data)


@app.route('/sources')
def sources():
    return render_template('home.html')


@app.route('/compiling')
def compiling():
    return render_template('home.html')


@app.route('/queue')
@app.route('/queue/<string:qtype>')
def queue(qtype = "all"):
    def depfind(packages):
        deplist = {}
        for p in packages:
            for repoid, repo  in  repos.items():
                try:
                    if p.paket.adi in repo.paketler.keys():
                        deplist[p.paket.adi] = repo.depcheck(p.paket.adi)
                except:
                    print("sorunlu paket ", p.paket.adi)
                    tb.print_exc()
                    pass
        return deplist
    deps = {}
    limit=200
    if qtype == "all":
        vals = ses.query(Kuyruk).filter(Kuyruk.durum < 1000).join(Paket).order_by(Kuyruk.id.desc()).limit(limit).all()
        deps = depfind(vals)
        return render_template('queue.html', packages = vals, build_deps = deps)
    else:
        qs = qtype.split(",")
        durumlar = []
        for durum in qs:
            durum = durum.strip().lower()
            if durum == "waiting":
                durumlar.append(0)
            if durum == "partial":
                durumlar.append(1)
            if durum == "waitingdep": 
                durumlar.append(2)
            if durum == "running":
                durumlar.append(100)
            if durum == "failed":
                durumlar.append(101)
            if durum == "success":
                durumlar.append(999)
        try:
            vals = ses.query(Kuyruk).filter(Kuyruk.durum.in_(durumlar)).join(Paket).order_by(Kuyruk.id.desc()).limit(limit).all()
            deps = depfind(vals)
        except:
            import traceback as tb
            return tb.format_exc()
        return render_template('queue.html', packages = vals, build_deps = deps)

@app.route('/queue/return2/<int:id>')
def queue_return(id):
    #FIXME: eger saglanmamis bagimlilik varsa, burada kontrol edilmeli
    q = ses.query(Kuyruk)
    q = q.filter(Kuyruk.id == id)
    rec = q.one()
    rec.durum = 0
    ses.flush()
    return "<html><script> window.history.back(); </script></html>"

@app.route('/queue/delete2/<int:id>')
def queue_delete(id):
    #FIXME: eger saglanmamis bagimlilik varsa, burada kontrol edilmeli
    q = ses.query(Kuyruk)
    q = q.filter(Kuyruk.id == id)
    rec = q.one()
    rec.durum = 5000
    ses.flush() 
    return "<html><script> window.history.back(); location.reload();</script></html>"
    #return "<html><script>window.location = 'https://ciftlik.pisilinux.org/ciftlik/queue/running'</script></html>"

@app.route('/farmlogin')
def farmlogin():
	return render_template('giris.html')

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
            vals = ses.query(Kuyruk).filter(Kuyruk.paket_id==paketID(pkgname)).join(Paket).order_by(Kuyruk.id.desc()).all()
            
            return render_template('pkgdetail.html', repo = [repo], stat = stat, pkg = pkg, commits = vals)
    else:
        try:
            repo = ses.query(Repo).all()
            
        except:
            ses.rollback()
        finally:
            repo = ses.query(Repo).all()
            pass

        perfdetail = perf.report()

   
        return render_template('home.html', repo = repo, stat = stat, perf = perfdetail) 

@app.route('/farmadmin')
def admin():
    repolar = ses.query(Repo).all()
    return render_template("admin.html", repo = repolar)


@app.route('/farmadmin/addrepo', methods=['GET', 'POST'])
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
            return "zaten varmis %d " % sayi
		
@app.route('/adduser')
def adduser():
	return render_template('admin_adduser.html')


@app.route('/requestPkg/<string:email>')
def requestPkg(email):
    try:
        gonullu_id = ses.query(Gonullu).filter(Gonullu.email == email).one().id
    except:
        cevap = {'state': states.MAILERR, 'durum': 'mail yok', 'mesaj': "ilkermanap@gmail.com adresine mektup atarak gonullu olmak istediginizi belirtin"}
        return jsonify(cevap)
    try:
        kuyruk = ses.query(Kuyruk).filter(Kuyruk.durum == 0 ).order_by(Kuyruk.id.asc()).first()
        k = ses.query(Kuyruk)
        k = k.filter(Kuyruk.id == kuyruk.id)
        kayit = k.one()
    except:
        cevap = {'state': states.NOPACKAGE, 'message':'No package in queue', 'durum': 'paket yok', 'mesaj':'Daha fazla bekleyin'}
        return jsonify(cevap)
    kayit.durum = 100
    ses.flush()
    yeniGorev = Gorev(gonullu_id=gonullu_id, kuyruk_id = kuyruk.id)
    ses.add(yeniGorev)
    ses.flush()
    docker_image = docker_image_name(kuyruk.repository, kuyruk.branch)
    repobinary = ""
    for repoid, r in repos.items():
        if (r.repo == kuyruk.repository) and (r.branch == kuyruk.branch):
            repobinary = r.binary_repo_dir
    
    paketadi = ses.query(Paket).filter(Paket.id == kuyruk.paket_id).first().adi
    ses.commit()
    krn = False
    if paketadi in blacklist:
        krn = True
    if docker_image is not None:
        cevap = {'state': states.OK, 'durum': 'ok','kuyruk_id': kuyruk.id, 'queue_id':kuyruk.id, 'paket': paketadi, 'package':paketadi, 'commit_id':kuyruk.commit_id, 'repo': kuyruk.repository, 'branch': kuyruk.branch , 'kernel_required':krn, 'kernel_gerekli': krn, 'dockerimage':docker_image , 'binary_repo_dir':repobinary}
        print(">>>>> ", cevap)
        return jsonify(cevap)
    else:
        cevap = {'state': states.NODOCKERIMAGE, 'message' : 'No docker image set for repository %s  branch %s' % (kuyruk.repository, kuyruk.branch) }
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
    return "OK"

@app.route('/performance/', methods = ['POST','GET'])
def perf_mon():
    return "Deneme"

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
    if p.reindex == True:
        rp = ses.query(Repo).all()
        for r in rp:
            repos[r.id] = RepoView(r, True, pisi20repo)

    d = p.db()
    bra = p.ref
    rep = p.data['repository']["full_name"].replace("https://github.com/", "")
    if check_branch_db(rep, bra) == True:
        tar = p.data['repository']['updated_at']
        tar = tar.replace("Z","").replace("T"," ")
        t = datetime.strptime(tar,"%Y-%m-%d %H:%M:%S")
        for _id, com in p.db2().items():
            print( "gitcommit, com.modified :",com['modified'])
            id = com['id']
            url = com['url']
            print(com['timestamp'], len(com['modified']))
            for pkg in com['modified']:
                pkg = pkg.strip()
                pkgid = paketID(pkg)
                if pkgid == None:
                    ppp = Paket(adi=pkg, aciklama="%s icin aciklama eklenmeli" % pkg)
                    ses.add(ppp)
                    ses.commit()
                    pkgid = paketID(pkg)
                if commitCheck(pkgid, id) == 0:
                    deplist = []
                    for repoid, repo  in  repos.items():
                        if pkg in repo.paketler.keys():
                            deplist = repo.depcheck(pkg)
                    drm = 0
                    state = True
                    for dep in deplist:
                        state = state and dep
                    if state == False:
                        drm = 2
                    k = Kuyruk(tarih=t, paket_id=pkgid, commit_id=id, \
                                      commit_url=url, durum=drm, repository=rep, \
                                      branch=bra)
                    ses.add(k)
                    ses.commit() 
                    ses.flush()
                else:
                    print(pkg, "  sorun var")
        return p.ref
    return p.ref


@app.route('/upload', methods = ['POST'])
def upload():
    import os
    if request.method == 'POST':
        file = request.files['file']
        repo_bin_path = request.form['binrepopath']
        print("repo_bin_path = ", repo_bin_path)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename_kalan = filename[filename.find("-")+1:]
            gercek_isim = filename_kalan[filename_kalan.find("-")+1:]
            kuyruk_id = int(filename.split("-")[0])
            k = ses.query(Kuyruk).filter(Kuyruk.id == kuyruk_id).first()
            pa = ses.query(Paket).filter(Paket.id == k.paket_id).first().adi
            trh = datetime.strftime(datetime.now(),"%Y%m%d")
            if pa[:3] == "lib":
                # lib ile basliyorsa
                pre = pa[:4]
            else:
                pre = pa[0]
            pkgdir = "%s/%s/%s-%s/" % (pre, pa, kuyruk_id ,k.commit_id)
            p = "%s/%s/%s/%s" % (REPOBASE, k.repository, k.branch, pkgdir)
            print("olusturulacak dizin : ", p)
            os.system("mkdir -p %s" % p)
            f = os.path.join(p, gercek_isim)
            file.save(f)
            hash = os.popen("sha1sum %s" % f, "r").readlines()[0].split()[0].strip()
            if f.endswith("pisi"):
                index = DockerIndexer(f, repo_bin_path)
            return hash 


@app.route("/compiledetail/<int:id>")
def compiledetail(id):
    k = ses.query(Kuyruk).filter(Kuyruk.id == id).first()
    paket = ses.query(Paket).filter(Paket.id == k.paket_id).first().adi
    if paket[:3] == "lib":
        ilk = paket[:4]
    else:
        ilk = paket[0]
    return render_template("compiledetail.html", paket=paket, kuyruk = k, ilk=ilk)