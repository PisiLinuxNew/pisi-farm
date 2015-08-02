import urllib2
import os
import json
import glob
import time

import requests

EMAIL = "ilkermanap@gmail.com"


def hafiza():
    """
    [en] return physical and swap memory in megabytes
    [tr] fiziksel ve takas hafiza boyu, megabyte olarak
    """
    mem = int(os.popen("free -m | grep Mem").readlines()[0].split()[1])
    swp = int(os.popen("free -m | grep Swap").readlines()[0].split()[1])
    return mem, swp


class DockerParams:
    """
    [tr] default durumda, sistem hafizasinin yarisi, takasin tamami docker
    tarafindan kullanilabilir.

    islemci %50

    [en] In default, docker will use half of the system memory, and no limit
    on swap

    cpu %50,
    """

    def __init__(self):
        self.sistem_hafiza, self.sistem_takas = hafiza()
        self.docker_hafiza = self.sistem_hafiza / 2
        self.docker_takas = -1
        self.cpu_kota = 0.5
        self.cpu_period = 100000
        self.cpu_quota = self.cpu_kota * self.cpu_period
        self.volumes = {}
        self.name = ""

    def set_hafiza(self, yeni_docker_hafiza, yeni_docker_takas):
        self.docker_hafiza = yeni_docker_hafiza
        self.docker_takas = yeni_docker_takas

    def set_cpu(self, yeni_cpu_orani):
        """
        [tr] yeni_cpu_orani 0 ile 1 arasinda float bir sayi olacaktir. 0 verilirse, en dusuk %10 yapilacaktir.
        [en] yeni_cpu_orani will be a float value between 0 and 1. If it is given less then %10, it will be %10.
        """
        if yeni_cpu_orani < 0.1:
            yeni_cpu_orani = 0.1
        self.cpu_kota = yeni_cpu_orani
        self.cpu_quota = self.cpu_kota * self.cpu_period

    def volume(self, local, indocker):
        self.volumes[indocker] = local

    def volumes_str(self):
        temp = ""
        for ind, local in self.volumes.items():
            temp += " -v %s:%s " % (local, ind)
        return temp

    def mem_str(self):
        temp = ""
        if self.docker_takas > -1:
            temp = " --memory-swap %dM " % self.docker_takas
        if self.docker_hafiza > -1:
            temp += " -m %dM " % self.docker_takas
        return temp

    def cpu_str(self):
        return " --cpu-period=%d --cpu-quota=%d " % (self.cpu_period, self.cpu_quota)

    def name_str(self):
        if self.name == "":
            return ""
        else:
            return "--name %s-sil" % self.name

    def param_str(self, extra=""):
        if self.name == "":
            return None
        return "%s %s %s %s %s " % (self.name_str(), self.cpu_str(), self.mem_str(), self.volumes_str(), extra)


class Docker:
    def __init__(self):
        self.started = self.start()
        self.image = ""
        self.id = None
        self.params = DockerParams()
        self.params.volume('/var/cache/pisi/packages': '/var/cache/pisi/packages')
        self.params.volume('/var/cache/pisi/archives': '/var/cache/pisi/archives')
        # TODO: derle dizini uygulamanin kuruldugu yerde olmali.. boylece kullaniciya kopyalatmayiz.
        # TODO: ya da
        self.params.volume('/derle': '/tmp/derle')

    def set_image_name(self, newname):
        self.image = newname
        self.retrieve()

    def retrieve(self):
        if self.image != "":
            if self.check() == 0:
                cmd = "docker pull %s" % self.image
                os.system(cmd)

    def rm(self, imgname):
        cmd = "docker rm %s"  % imgname
        status = os.system(cmd)
        return status

    def check(self):
        cmd = "docker ps >/dev/null"
        status = os.system(cmd)
        return status

    def run(self, extra_params = ""):
        prm = self.params.param_str(extra_params)

    def start(self):
        if self.check() != 0:
            print "Starting docker"
            cmd1 = "sudo cgroupfs-mount"
            cmd2 = "docker -d &"
            print "Mounting cgroupfs"
            stat1 = os.system(cmd1)
            print "Starting docker daemon"
            stat2 = os.system(cmd2)
            if stat2 == 0:
                return True
        else:
            print "Docker already started"
            return True
        return False


class Paketci:
    def __init__(self, dock, docker_imaj_adi=None):
        self.docker = dock
        self.basari = None
        self.docker_imaj_adi = docker_imaj_adi


    def calisma_kontrol(self):
        cmd = "ls /tmp/%s/%s.bitti" % (self.paket, self.paket)
        status = os.system(cmd)
        if status == 0:
            self.basari = int(open("/tmp/%s/%s.bitti" % (self.paket, self.paket), "r").readlines()[0])
        return status, self.basari

    def derle_yerel(self):
        # TODO: yerel paket tanimi gerek,
        self.farm_paket_al()
        cmd = "docker run -id --name %s-sil %s %s /derle/derle.sh %s %s %s" % \
              (self.paket, self.volumes_str(), self.dockerImageName, self.kuyruk_id, self.commit_id, self.paket)
        print cmd
        status = os.system(cmd)
        calisiyor = True
        while calisiyor:
            time.sleep(10)
            calisma, basari = self.calisma_kontrol()
            if calisma == 0:
                calisiyor = False
                time.sleep(5)
                cmd = "updaterunning?id=%s&state=%s" % (self.kuyruk_id, basari)
                self.farm.get(cmd)
                return
            print "hala calisiyor"

class Gelistirici(Paketci):
    def __init__(self, dock):
        Paketci.__init__(self, dock)
        self.pspec = ""

    def set_pspec(self, pspec):
        self.pspec = pspec

    

class Gonullu(Paketci):
    def __init__(self, farm, dock):
        Paketci.__init__(self, dock)
        self.farm = farm
        self.commit_id = None
        self.kuyruk_id = None
        self.repo = None
        self.branch = None
        self.derle()
        self.gonder()

    def farm_paket_al(self, email = EMAIL):
        d = self.farm.kuyruktan_paket_al(email)
        self.paket = d['paket']
        self.docker.params.name = self.paket
        self.repo = d['repo']
        self.branch = d['branch']
        self.docker_imaj_adi = self.farm.docker_adi(d['repo'], d['branch'])
        self.docker.set_image_name(self.docker_imaj_adi)
        self.commit_id = d['commit_id']
        self.kuyruk_id = d['kuyruk_id']
        self.docker.params.volume('/tmp/%s' % self.paket, "/root")

    def gonder(self):
        liste = glob.glob("/tmp/%s/*.[lpe]*" % self.paket)
        print liste
        self.farm.dosyalari_gonder(liste, self.repo, self.branch)
        if  not self.docker.rm("%s-sil" % self.paket):
            print "imaj silinemedi ", self.paket
        tmptemizle = "rm -rf /tmp/%s" % self.paket
        os.system(tmptemizle)

    def derle(self):
        self.farm_paket_al()
        cmd = "docker run -id --name %s-sil %s %s /derle/derle.sh %s %s %s" % \
              (self.paket, self.volumes_str(), self.dockerImageName, self.kuyruk_id, self.commit_id, self.paket)
        print cmd
        status = os.system(cmd)
        calisiyor = True
        while calisiyor:
            time.sleep(10)
            calisma, basari = self.calisma_kontrol()
            if calisma == 0:
                calisiyor = False
                time.sleep(5)
                cmd = "updaterunning?id=%s&state=%s" % (self.kuyruk_id, basari)
                self.farm.get(cmd)
                return
            print "hala calisiyor"

class Farm:
    def __init__(self, farm_url):
        self.url = farm_url
        self.params = self.parametre()

    def get(self, cmd):
        return urllib2.urlopen("%s/%s" % (self.url, cmd)).read()

    def kuyruktan_paket_al(self, email):
        cmd = "requestPkg/%s" % email
        return json.loads(self.get(cmd))

    def parametre(self):
        bilgi = self.get("parameter")
        return json.loads(bilgi)

    def docker_adi(self, repo, branch):
        for r in self.params:
            if (r['repo'] == repo) and (r['branch'] == branch):
                return r['dockerimage']
        return None

    def dosya_gonder(self, fname, r, b):
        cmd = "upload"
        f = {'file': open(fname, 'rb')}
        r = requests.post("%s/%s" % (self.url, cmd), files=f)
        hashx = os.popen("sha1sum %s" % fname, "r").readlines()[0].split()[0].strip()
        if hashx == r.text.strip():
            return True
        else:
            return False

    def dosyalari_gonder(self, liste, repo, branch):
        for f in liste:
            print "dosya gonderiliyor, ", f
            if self.dosya_gonder(f, repo, branch):
                print f, " gonderildi"
        print liste


d = Docker()
f = Farm("http://ciftlik.pisilinux.org/ciftlik")
g = Gonullu(f, d)

"""
docker run -itd 
-v /home/packages:/var/cache/pisi/packages 
-v /home/archives:/var/cache/pisi/archives 
-v /home/ertugrul/Works/manap_se/build:/root 
-v /home/ertugrul/Works/PisiLinux:/git 
ertugerata/pisi-chroot-farm bash 
"""
