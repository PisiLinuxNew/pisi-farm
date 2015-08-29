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


class RepoView:
    def __init__(self, r, init = False):
        self.id = r.id
        self.repo = r.repo
        self.branch = r.branch
        self.dockerimage = r.dockerimage
        self.repourl = r.repourl
        self.repofile = self.repourl.split("/")[-1]
        self.repodir = REPOBASE +"/" +  self.repo
        self.enable = r.enable
        self.yapi = ""
        self.repoacik = ("%s/%s" % (self.repodir, self.repofile)).replace(".xz","")
        self.paketler = {}
        self.build_dep = {}
        self.run_dep = {}
        if init == True:
            self.init()
        else:
            self.xmlOku()
        print self.id, self.repo, self.branch, self.dockerimage, self.repodir, self.repourl, self.enable


    def info(self):
        temp = {}
        temp['repo'] = self.repo
        temp['branch'] = self.branch
        temp['dockerimage'] = self.dockerimage
        temp['repourl'] = self.repourl
        temp['id'] = self.id
        return temp


    def xmlOku(self):
        self.yapi = objectify.fromstring(open(self.repoacik,"r").read())
        self.paketler = {}
        for p in self.yapi.iterchildren():
            if (p.tag == "SpecFile"):
                self.paketler[p.Source.Name] = p

        for pname, pkg  in self.paketler.items():
            for t in pkg.iterchildren():
                if t.tag == "BuildDependencies":
                    for dep in t.iterchildren():
                        if dep.tag == "Dependency":
                            if pname not in self.build_dep:
                                self.build_dep[pname] = [dep]
                            elif dep not in self.build_dep[pname]:
                                self.build_dep[pname].append(dep)
        for k,v in self.build_dep.items():
            print k, v

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
        os.system("mkdir -p %s" % self.repodir)
        self.checkHash()
        self.xmlOku()

    def checkHash(self):
        """
        Repo hash degerini internette olan ile kontrol ederek, yenisi cikmis ise
        repoyu yeniler.
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

repos = {}
rp = ses.query(Repo).all()
for r in rp:
    repos[r.id] = RepoView(r, True)


if __name__ == "__main__":
    for rid, r in  repos.items():
        for k,v in r.paketler.items():
            print k,  r.pkgDesc(v)

