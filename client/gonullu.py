import urllib2
import os
import json
import requests, sys

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

    def dosya_gonder(self):
        cmd = "upload"
        fname = "to be described"
        f = {'file': open(fname, 'rb')}                


        r = requests.post("%s/%s" % (self.url, cmd) , files = f)
        hash = os.popen("sha1sum %s" % sys.argv[1], "r").readlines()[0].split()[0].strip()
        if hash == r.text.strip():
            return True
        else:
            return False




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

    def gonder(self):





d = Docker()
f = Farm("http://manap.se:5000")
g = Gonullu(f,d)



r = requests.post("http://manap.se:5000/upload", files = f)
hash = os.popen("sha1sum %s" % sys.argv[1], "r").readlines()[0].split()[0].strip()
if hash == r.text.strip():
    print "gonderim basarili"
    os.system("rm -rf %s" % sys.argv[1])

