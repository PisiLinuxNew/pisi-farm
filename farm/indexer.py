import os
from gonullu import hafiza,Docker,DockerParams


#TODO: repopath aslinda /var/www/testrepo/pisi-2.0-test olmali, ama uzerinde dusunmeli.
#/usr/bin/docker run -i --rm -v /var/www/vhosts/pisilinux.org/ciftlik/2.0-Beta.1:/root ertugerata/pisi-chroot-index  index . --skip-signing > /dev/null;
REPOPATH  = "/var/www/vhosts/pisilinux.org/ciftlik"
#BASEIMAGE = "ertugerata/pisi-chroot-index"
BASEIMAGE = "pisilinux/chroot"
class DockerIndexer(Docker):
    def __init__(self, fname, binrepopath, baseimage = BASEIMAGE):
        Docker.__init__(self)
        self.repopath = "%s/%s" % (REPOPATH, binrepopath)
        os.system("cp %s %s/." % (fname, self.repopath ))
        self.params.volume(self.repopath, '/root')
        self.set_image_name(baseimage)
        self.run("pisi index . --skip-signing")

    def add_file(self, fname):
        os.system("cp %s %s/." % (fname, self.repopath))
        
    def add_files(self, files):
        for f in files:
            self.add_file(f)
    
    def start_index(self):
        self.run("pisi index . --skip-signing")
