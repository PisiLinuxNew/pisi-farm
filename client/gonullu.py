import urllib2
import os
import json


class Docker:
    def __init__(self):
        self.start()
        self.image = ""
        self.id = None

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

    def start():
        if self.check() != 0:
            print "starting docker"
            cmd1 = "sudo cgroupfs-mount"
            cmd2 = "docker -d &"
            os.system(cmd1)
            os.system(cmd2)
        else:
            print "docker already started"

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

class Gonullu:
    def __init__(self, farm, dock):
        self.farm = farm
        self.paket = None
        self.dockerImageName = self.farm.params['docker-image']
        self.derle()

    def paketAl(self):
        self.paket = self.farm.kuyruktanPaketAl()

    def derle(self):
        pkg = self.paketAl()
        cmd = "docker run -itd %s pisi bi -y  --ignore-safety %s" % (self.dockerImageName, self.paket)
        os.system(cmd)

d = Docker()
f = Farm("http://manap.se:5000")
g = Gonullu(f,d)

