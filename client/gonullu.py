mport urllib2
import os
import json
import requests, sys, glob, time
EMAIL = "ilkermanap@gmail.com"

class Docker:
    def __init__(self):
        self.started = self.start()
        self.image = ""
        self.id = None
        self.volumes = {}

    def setImageName(self, newName):
        self.image = newName

    def retrieve(self):
        if self.image != "":
            if self.check() == 0:
                cmd = "docker pull %s" % self.image
                os.system(cmd)

    def check(self):
        cmd = "docker ps >/dev/null"
        status = os.system(cmd)
        return status

    def volume(self, local, indocker):
        self.volumes[indocker] = local

    def start(self):
        if self.check() != 0:
            print "Starting docker"
            cmd1 = "sudo cgroupfs-mount"
            cmd2 = "docker -d &"
            print "Mounting cgroupfs"
            stat1 = os.system(cmd1)
            print "Starting docker daemon"
            stat2 = os.system(cmd2)
            if (stat2 == 0):
                return True
        else:
            print "Docker already started"
            return True
        return False

class Farm:
    def __init__(self, farm_url):
        self.url = farm_url
        self.params = self.parametre()


    def get(self, cmd):
        return urllib2.urlopen("%s/%s" % (self.url, cmd)).read()


    def kuyruktanPaketAl(self, email):
        cmd = "requestPkg/%s" % email
        return json.loads(self.get(cmd))


    def parametre(self):
        bilgi = self.get("parameter")
        return json.loads(bilgi)


    def docker_adi(self, repo, branch):
        for r in self.params:
            if ((r['repo'] == repo ) and (r['branch'] == branch)):
                return r['dockerimage']
        return None


    def dosya_gonder(self, fname, r, b):
        cmd = "upload"
        f = {'file' : open(fname, 'rb') }
        r = requests.post("%s/%s" % (self.url, cmd) , files = f)
        hash = os.popen("sha1sum %s" % fname, "r").readlines()[0].split()[0].strip()
        if hash == r.text.strip():
            return True
        else:
            return False


    def dosyalari_gonder(self, liste, repo, branch):
        # FIXME:  derleme islemi sonucunda olusan log ve pisi
        # dosyalari burada gonderilecek
        for f in liste:
            print "dosya gonderiliyor, ", f
            if self.dosya_gonder(f, repo, branch) == True:
                print f, " gonderildi"
        print liste


class Gonullu:
    def __init__(self, farm, dock):
        self.farm = farm
        self.paket = None
        self.dockerImageName = None 
        self.docker = dock
        self.commit_id = None
        self.kuyruk_id = None
        self.repo = None
        self.branch = None
        self.volumes = {'/var/cache/pisi/packages': '/var/cache/pisi/packages',
                        '/var/cache/pisi/archives': '/var/cache/pisi/archives',
                        '/derle':'/tmp/derle'}
        self.basari = None
        self.derle()
        self.gonder()


    def paketAl(self):
        d = self.farm.kuyruktanPaketAl("ilkermanap@gmail.com")
        self.paket = d['paket']
        self.repo = d['repo']
        self.branch = d['branch']
        self.dockerImageName = self.farm.docker_adi(d['repo'], d['branch'])
        self.docker.setImageName(self.dockerImageName)
        self.docker.retrieve()
        self.commit_id = d['commit_id']
        self.kuyruk_id = d['kuyruk_id']
        self.volumes['/root'] = '/tmp/%s' % ( self.paket)


    def volumes_str(self):
        temp = ""
        for ind, local in self.volumes.items():
            temp += " -v %s:%s " % (local, ind)
        return temp


    def calisma_kontrol(self):
        cmd = "ls /tmp/%s/%s.bitti" % (self.paket, self.paket)
        status = os.system(cmd)
        if status == 0:
            self.basari = int(open("/tmp/%s/%s.bitti" % (self.paket, self.paket), "r").readlines()[0])
        return (status, self.basari)


    def derle(self):
        self.paketAl()
        cmd = "docker run -id --name %s-sil %s %s /derle/derle.sh %s %s %s" % ( self.paket,  self.volumes_str(), self.dockerImageName, self.kuyruk_id, self.commit_id, self.paket)
        print cmd
        status = os.system(cmd)
        calisiyor = True
        while calisiyor:
            time.sleep(10)
            calisma , basari =  self.calisma_kontrol()
            if calisma == 0:
                calisiyor = False
                time.sleep(5)
                cmd = "updaterunning?id=%s&state=%s" % (self.kuyruk_id, basari)
                self.farm.get(cmd)
                return
            print "hala calisiyor"


    def gonder(self):
        liste = glob.glob("/tmp/%s/*.[lpe]*" % self.paket)
        print liste
        self.farm.dosyalari_gonder(liste, self.repo, self.branch)
        temizle = "docker rm %s-sil" % self.paket
        os.system(temizle)
        tmptemizle = "rm -rf /tmp/%s" % self.paket
        os.system(tmptemizle)


d = Docker()
f = Farm("http://ciftlik.pisilinux.org/ciftlik")
g = Gonullu(f,d)

"""
docker run -itd 
-v /home/packages:/var/cache/pisi/packages 
-v /home/archives:/var/cache/pisi/archives 
-v /home/ertugrul/Works/manap_se/build:/root 
-v /home/ertugrul/Works/PisiLinux:/git 
ertugerata/pisi-chroot-farm bash 
"""
