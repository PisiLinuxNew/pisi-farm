import urllib2
import os
import json
import glob
import time

import requests

EMAIL = "ilkermanap@gmail.com"


def hazirlik(kernel_gerekli):
    krn = " "
    if kernel_gerekli == True:
        krn = " kernel "
    derlesh = """#!/bin/bash
service dbus start && pisi cp && pisi ar pisi-2.0 https://ciftlik.pisilinux.org/pisi-2.0/pisi-index.xml.xz && pisi it --ignore-safety --ignore-dependency autoconf autogen automake binutils bison flex gawk gc gcc gnuconfig guile libmpc libtool-ltdl libtool lzo m4 make mpfr pkgconfig yacc glibc-devel %s
pisi ar core https://github.com/pisilinux/core/raw/master/pisi-index.xml.xz && pisi ar main https://github.com/pisilinux/main/raw/master/pisi-index.xml.xz --at 2
pisi ur
cd /root
pisi bi --ignore-safety -y $3 1>$1-$2-$3.log 2>$1-$2-$3.err
STAT=$?
for s in `ls *.pisi`
do
  mv $s $1-$2-$s
done
echo $STAT >  $3.bitti
""" % krn

    gelistirsh = """#!/bin/bash
# birinci paket adi,
# ikinci pspec adresi
service dbus start && pisi cp && pisi ar pisi-2.0 https://ciftlik.pisilinux.org/pisi-2.0/pisi-index.xml.xz && pisi it --ignore-safety --ignore-dependency autoconf autogen automake binutils bison flex gawk gc gcc gnuconfig guile libmpc libtool-ltdl libtool lzo m4 make mpfr pkgconfig yacc glibc-devel %s
pisi ar core https://github.com/pisilinux/core/raw/master/pisi-index.xml.xz && pisi ar main https://github.com/pisilinux/main/raw/master/pisi-index.xml.xz --at 2
pisi ur
cd /root
pisi bi --ignore-safety -y $2 1>$1.log 2>$1.err
STAT=$?
echo $STAT >  $1.bitti
""" % krn
    os.system("mkdir -p /tmp/derle")
    f = open("/tmp/derle/derle.sh","w")
    f.write(derlesh)
    f.close()
    f = open("/tmp/derle/gelistirici.sh","w")
    f.write(gelistirsh)
    f.close()
    os.system("chmod 755 /tmp/derle/*.sh")


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
        self.cpu_kota = 1
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
        if yeni_cpu_orani > 1:
            yeni_cpu_orani = 1
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
            temp += " -m %dM " % self.docker_hafiza
        return temp

    def cpu_str(self):
        return " --cpu-period=%d --cpu-quota=%d " % (self.cpu_period, self.cpu_quota)

    def name_str(self):
        if self.name == "":
            return ""
        else:
            return "--name %s-sil" % self.name

    def param_str(self, extra="", image=""):
        if self.name == "":
            return None
        return "%s %s %s %s %s %s " % (self.name_str(), self.cpu_str(), self.mem_str(),
                                       self.volumes_str(), image, extra)


class Docker:
    def __init__(self):
        self.started = self.start()
        self.image = ""
        self.id = None
        self.params = DockerParams()
        #self.params.volume('/var/cache/pisi/packages', '/var/cache/pisi/packages')
        #self.params.volume('/var/cache/pisi/archives', '/var/cache/pisi/archives')
        # TODO: derle dizini uygulamanin kuruldugu yerde olmali.. boylece kullaniciya kopyalatmayiz.
        # TODO: ya da
        self.params.volume('/tmp/derle', '/derle')

    def set_image_name(self, newname):
        self.image = newname
        self.retrieve()

    def retrieve(self):
        if self.image != "":
            if self.check() == 0:
                cmd = "docker pull %s" % self.image
                os.system(cmd)

    def rm(self, imgname):
        cmd = "docker rm %s" % imgname
        status = os.system(cmd)
        return status

    def check(self):
        cmd = "docker ps >/dev/null"
        status = os.system(cmd)
        return status

    def run(self, extra_params=""):
        prm = "sudo docker run -id  %s " % (self.params.param_str(extra_params, self.image))
        print prm
        return prm

    def start(self):
        if self.check() != 0:
            print "Starting docker"
            #cmd1 = "sudo cgroupfs-mount"
            cmd2 = "docker -d &"
            #print "Mounting cgroupfs"
            #stat1 = os.system(cmd1)
            print "Starting docker daemon"
            stat2 = os.system(cmd2)
            if stat2 == 0:
                return True
        else:
            print "Docker already started"
            return True
        return False


class DockerGonullu(Docker):
    def __init__(self):
        Docker.__init__(self)
        self.params.volume('/var/cache/pisi/packages', '/var/cache/pisi/packages')
        self.params.volume('/var/cache/pisi/archives', '/var/cache/pisi/archives')
        self.params.volume('/tmp/derle', '/derle')

class Paketci:
    def __init__(self, dock, docker_imaj_adi=None):
        self.docker = dock
        self.basari = None
        self.docker_imaj_adi = docker_imaj_adi
        self.paket = None
        self.kernel_gerekli = None

    def set_paket(self, yeni_paket):
        self.paket = yeni_paket

    def calisma_kontrol(self):
        cmd = "ls /tmp/%s/%s.bitti" % (self.paket, self.paket)
        status = os.system(cmd)
        if status == 0:
            self.basari = int(open("/tmp/%s/%s.bitti" % (self.paket, self.paket), "r").readlines()[0])
        return status, self.basari


class Gelistirici(Paketci):
    def __init__(self, dock):
        Paketci.__init__(self, dock)
        self.pspec = ""

    def set_pspec(self, pspec):
        self.pspec = pspec

    def farm_paket_al(self, email=EMAIL):
        d = self.farm.kuyruktan_paket_al(email)
        self.paket = d['paket']
        self.docker.params.name = self.paket
        self.repo = d['repo']
        self.branch = d['branch']
        self.docker_imaj_adi = self.farm.docker_adi(d['repo'], d['branch'])
        self.docker.set_image_name(self.docker_imaj_adi)
        self.commit_id = d['commit_id']
        self.kuyruk_id = d['kuyruk_id']
        self.kernel_gerekli = d['kernel_gerekli']
        self.docker.params.volume('/tmp/%s' % self.paket, "/root")

    def derle(self):
        self.farm_paket_al()
        extra = "/derle/derle.sh %s %s %s" % (self.kuyruk_id, self.commit_id, self.paket)
        cmd = self.docker.run(extra)
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

    def farm_paket_al(self, email=EMAIL):
        d = self.farm.kuyruktan_paket_al(email)
        self.paket = d['paket']
        self.docker.params.name = self.paket
        self.repo = d['repo']
        self.branch = d['branch']
        self.docker_imaj_adi = self.farm.docker_adi(d['repo'], d['branch'])
        self.docker.set_image_name(self.docker_imaj_adi)
        self.commit_id = d['commit_id']
        self.kernel_gerekli = d['kernel_gerekli']
        hazirlik(self.kernel_gerekli)
        self.kuyruk_id = d['kuyruk_id']
        self.docker.params.volume('/tmp/%s' % self.paket, "/root")

    def gonder(self):
        liste = glob.glob("/tmp/%s/*.[lpe]*" % self.paket)
        print liste
        self.farm.dosyalari_gonder(liste, self.repo, self.branch)
        if self.docker.rm("%s-sil" % self.paket) != 0:
            print "imaj silinemedi ", self.paket
        tmptemizle = "rm -rf /tmp/%s" % self.paket
        os.system(tmptemizle)

    def derle(self):
        self.farm_paket_al()
        extra = "/derle/derle.sh %s %s %s" % (self.kuyruk_id, self.commit_id, self.paket)
        cmd = self.docker.run(extra)
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
        ek = ""
        if fname.split(".")[-1] in ("err","log"):
            icerik = open(fname,"r").read()
            htm = open("%s.html" % fname, "w")
            htm.write("<html><body><pre>")
            htm.write(icerik)
            htm.write("</pre></body></html>")
            htm.close()
            ek = ".html"
        f = {'file': open("%s%s" % (fname, ek) , 'rb')}
        r = requests.post("%s/%s" % (self.url, cmd), files=f)
        hashx = os.popen("sha1sum %s%s" % (fname, ek), "r").readlines()[0].split()[0].strip()
        print ">> uzak hash   : %s"  % r.text.strip()
        print ">> yakin hash  : %s"  % hashx

        if hashx == r.text.strip():
            return True
        else:
            return False

    def dosyalari_gonder(self, liste, repo, branch):
        for f in liste:
            print "dosya gonderiliyor, ", f
            if self.dosya_gonder(f, repo, branch):
                print f, " gonderildi"
            else:
                while not(self.dosya_gonder(f, repo, branch)):
                    print f, " deniyoruz"
                    time.sleep(5)


        print liste


if __name__ == "__main__":
    d = DockerGonullu()
    f = Farm("https://ciftlik.pisilinux.org/ciftlik")
    #f = Farm("http://ciftlik.pisilinux.org:5000")
    while 1:
        g = Gonullu(f, d)
        for i in range(10):
            print "Kalan %d sn. Durdurmak icin simdi ctrl-c ile kesebilirsiniz.." % ((10 - i) * 3)
            time.sleep(3)

"""
docker run -itd 
-v /home/packages:/var/cache/pisi/packages 
-v /home/archives:/var/cache/pisi/archives 
-v /home/ertugrul/Works/manap_se/build:/root 
-v /home/ertugrul/Works/PisiLinux:/git 
ertugerata/pisi-chroot-farm bash 
"""
