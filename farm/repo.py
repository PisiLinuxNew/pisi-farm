__author__ = 'ilker'

from lxml import objectify 
from model import *
import urllib2, os

REPOS = {'0':{'repo' : 'pisilinux/core',
          'branch' : 'master',
          'dockerimage' : 'ertugerata/pisi-chroot-farm',
          'repo_dir' : '/var/www/html/pisilinux-core',
          'upload' : "/var/www/html/pisi-upload/",
          'repo_url' : 'https://github.com/pisilinux/core/raw/master/pisi-index.xml.xz' }}

TEST="test"

REPOBASE = "/var/www/testrepo"

class RepoBase:
    def __init__(self, repo =  "reponame", repourl = None, init = False):
        self.repourl = repourl
        self.repo = repo
        self.repodir = REPOBASE +"/" +  self.repo
        self.repofile = self.repourl.split("/")[-1]
        self.repoacik = ("%s/%s" % (self.repodir, self.repofile)).replace(".xz","")
        self.paketler = {}
        self.run_dep = {}
        self.yapi = ""

    def init(self):
        os.system("mkdir -p %s" % self.repodir)
        self.checkHash()

    def checkHash(self):
        """
        Repo hash degerini internette olan ile kontrol ederek, yenisi cikmis ise repoyu yeniler.
        """
        import urllib2
        repofile = self.repourl.split("/")[-1]
        if os.path.exists("%s/%s.sha1sum" % (self.repodir, repofile)):
            yeniHash = urllib2.urlopen("%s.sha1sum" % self.repourl).readlines()[0]
            eskiHash = open("%s/%s.sha1sum" % (self.repodir, repofile)).readlines()[0]
            if yeniHash.strip() != eskiHash.strip():
                self.retrieve()
                f = open("%s/%s.sha1sum" % (self.repodir, repofile),"w")
                f.write(yeniHash)
                f.close()
            else:
                if not (os.path.exists("%s/%s" % (self.repodir, repofile))):
                    self.retrieve()
        else:
            yeniHash = urllib2.urlopen("%s.sha1sum" % self.repourl).readlines()[0]
            self.retrieve()
            f = open("%s/%s.sha1sum" % (self.repodir, repofile) ,"w")
            f.write(yeniHash)
            f.close()

    def retrieve(self):
        """
        Repo icin pisi-index.xml.xz dosyasini getirir. repoadi.pisi-index.xml.xz
        olarak getirip, ardindan  dosyayi acar.                                                                          
        """
        repofile = self.repourl.split("/")[-1]
        os.system("wget %s -O %s/%s" % (self.repourl, self.repodir, repofile))
        os.system("xz --keep -f -d %s/%s" % (self.repodir,repofile))

class RepoBinary(RepoBase):
    def __init__(self, repo = "reponame", repourl = None, init = False):  
        RepoBase.__init__(self, repo, repourl, init)
        self.versiyonlar = {}
        self.init()
        self.xml_oku()

    def xml_oku(self):
        self.yapi = objectify.fromstring(open(self.repoacik,"r").read())
        self.paketler = {}
        self.versiyonlar = {}
        for p in self.yapi.iterchildren():
            if p.tag == "Package":
                self.paketler[p.Name] = p
                maxhist = 0
                vers = 0
                for hist in p.History.iterchildren():
                    if hist.tag == "Update":
                        if "release" in hist.attrib.keys():
                            hst = int(hist.attrib["release"])
                            if hst > maxhist:
                                maxhist = hst
                                vers = hist.Version
                self.versiyonlar[p.Name] = vers
                print p.Name, maxhist, vers


class RepoView(RepoBase):
    def __init__(self, r, init = False, binrepo = None):
        RepoBase.__init__(self, repo = r.repo, repourl = r.repourl )
        self.binary_repo = binrepo
        self.id = r.id
        self.repo = r.repo
        self.branch = r.branch
        self.dockerimage = r.dockerimage
        self.repourl = r.repourl

        self.repodir = REPOBASE +"/" +  self.repo
        self.enable = r.enable
        self.repoacik = ("%s/%s" % (self.repodir, self.repofile)).replace(".xz","")
        self.build_dep = {}
        if init == True:
            self.init()
        else:
            self.xmlOku()
        print self.id, self.repo, self.branch, self.dockerimage, self.repodir, self.repourl, self.enable

    def depcheck(self, pname):
        def vercheck(v1, v2):
            """
            1.2.42.a  gibi gelmis olan iki farkli versiyonu kontrol eder..
            v1 > v2  ise 1
            v1 = v2 ise 0
            v1 < v2 ise -1 
            """
            if v1 == v2:
                return 0
            else:
                v1p = v1.split(".")
                v2p = v2.split(".")
                n1 = len(v1p)
                if n1 < len(v2p):
                    n1 = len(v2p)
                
                for i in range(n1):
                    if int(v1p[i]) > int(v2p[i]):
                        return 1
                    elif int(v1p[i]) < int(v2p[i]):
                        return -1

        temp = {}
        vers = None
        if pname  in self.build_dep.keys():
            for p in self.build_dep[pname]:
                vers = None
                paket, state = p
                if paket.find(",") > 0:
                    pkt, vers = paket.split(",")
                else: 
                    pkt = paket
                if pkt in self.binary_repo.paketler.keys():
                    if vers != None:
                        print "!!!!! ",self.binary_repo.versiyonlar[pkt], vers                     
                        print "!!!!! ",type(self.binary_repo.versiyonlar[pkt]), type(vers)

                        vc = vercheck(str(self.binary_repo.versiyonlar[pkt]), vers)
                        if state == "eq":
                            if vc == 0:
                                temp[paket] = True
                                vers = None
                            else:
                                temp[paket] = False
                                vers = None
                        if state == "geq":
                            if vc in [0,1]:
                                temp[paket] = True
                                vers = None
                            else:
                                temp[paket] = False
                                vers = None
                    else:
                        temp[paket] = True
                else:
                    temp[paket] = False
            return temp
        else:
            return None

    def info(self):
        temp = {}
        temp['repo'] = self.repo
        temp['branch'] = self.branch
        temp['dockerimage'] = self.dockerimage
        temp['repourl'] = self.repourl
        temp['id'] = self.id
        return temp

    def xmlOku(self):
        def deps(pkg, tag):
            temp = []
            for t in pkg.Source.iterchildren():
                if t.tag == tag:
                    for dep in t.iterchildren():
                        if dep.tag == "Dependency":
                            state = ""
                            if len(dep.attrib.values()) > 0:
                                d = dep.attrib.keys()[0]
                                if d == "version":
                                    state = "eq"
                                #FIXME:   releaseFrom degil, versionFrom olmali..
                                # Paketcileri uyar
                                if ((d == "versionFrom") or (d == "releaseFrom")):
                                    state = "geq"
                                print "attrib.keys :", dep.attrib.keys()
                                
                                dep = dep + "," + dep.attrib.values()[0]
                            temp.append((dep, state))
            return temp

        self.yapi = objectify.fromstring(open(self.repoacik,"r").read())
        self.paketler = {}
        for p in self.yapi.iterchildren():
            if (p.tag == "SpecFile"):
                self.paketler[p.Source.Name] = p

        for pname, pkg  in self.paketler.items():
            deplistesi = deps(pkg, "BuildDependencies")
            if pname not in self.build_dep.keys():
                self.build_dep[pname] = deplistesi
            else:
                for dep in deplistesi:
                    if dep not in self.build_dep[pname]:
                        self.build_dep[pname].append(dep)

    def pkgDesc(self, pkg):
        temp = {}
        for t in pkg.Source.iterchildren():
            if t.tag == "Description":
                temp[t.attrib.values()[0]] = t
        return temp

    def pkginfo(self, pkgname):
        if pkgname in self.paketler:
            return self.paketler[pkgname]
        else:
            return None

    def init(self):
        RepoBase.init(self)
        self.xmlOku()

pisi20repo = RepoBinary("pisi-2.0-test", "http://ciftlik.pisilinux.org/pisi-2.0/pisi-index.xml.xz")

repos = {}
rp = ses.query(Repo).all()
for r in rp:
    repos[r.id] = RepoView(r, True, pisi20repo)




if __name__ == "__main__":
    for rid, r in  repos.items():
        for k,v in r.paketler.items():
            print k,  r.pkgDesc(v)

