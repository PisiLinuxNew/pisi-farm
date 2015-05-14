import urllib2
import os
import json
import requests, sys


class Docker:
    def __init__(self):
        self.started = self.start()
        self.image = ""
        self.id = None
        self.voluumes = {}

    def logs(self):
        pout = "docker.%s.stdout" % self.id
        perr = "docker.%s.stderr" % self.id

        os.mkfifo(pout)
        os.mkfifo(perr)
        self.out = open(pout)
        self.err = open(perr)

    def setImageName(self, newName):
        self.image = newName


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
            os.system(cmd1)
            print "Starting docker daemon"            
            os.system(cmd2)
        else:
            print "Docker already started"

class Farm:
    def __init__(self, farm_url):
        self.url = farm_url
        self.params = self.parametre()

    def get(self, cmd):
        return urllib2.urlopen("%s/%s" % (self.url, cmd)).read()

    def kuyruktanPaketAl(self):
        cmd = "requestPkg"
        return self.get(cmd)

    def parametre(self):
        bilgi = self.get("parameter")
        return json.loads(bilgi)

    def dosya_gonder(self, fname):
        cmd = "upload"
        f = {'file' : open(fname, 'rb') }
        r = requests.post("%s/%s" % (self.url, cmd) , files = f)
        hash = os.popen("sha1sum %s" % sys.argv[1], "r").readlines()[0].split()[0].strip()
        if hash == r.text.strip():
            return True
        else:
            return False

        
    def dosyalari_gonder(self, liste):
        # FIXME:  derleme islemi sonucunda olusan log ve pisi 
        # dosyalari burada gonderilecek
        for f in liste:
            if self.dosya_gonder(f) == True:
                liste.remove(f)

class Gonullu:
    def __init__(self, farm, dock):
        self.farm = farm
        self.paket = None
        self.dockerImageName = self.farm.params['docker-image']
        self.docker = dock
        self.volumes = {'/var/cache/pisi/packages': '/var/cache/pisi/packages',
                        '/var/cache/pisi/archives': '/var/cache/pisi/archives'}

        self.derle()

    def paketAl(self):
        self.paket = self.farm.kuyruktanPaketAl()
        self.volumes['/root'} = '%s/%s' % (os.environ['HOME'], self.paket)

    def volumes_str(self):
        temp = ""
        for ind, local in self.volumes.items():
            temp += " -v %s:%s " % (local, ind)
        return temp

    def derle(self):
        pkg = self.paketAl()
        cmd = "docker run -itd %s %s pisi bi -y  --ignore-safety %s 1>%s-build.log 2>%s-err.log" % (self.volumes_str(), self.dockerImageName, self.paket)
        status = os.system(cmd)
        

d = Docker()
f = Farm("http://manap.se:5000")
g = Gonullu(f,d)

"""
docker run -itd 
-v /home/packages:/var/cache/pisi/packages 
-v /home/archives:/var/cache/pisi/archives 
-v /home/ertugrul/Works/manap_se/build:/root 
-v /home/ertugrul/Works/PisiLinux:/git 
ertugerata/pisi-chroot-farm bash 
"""
