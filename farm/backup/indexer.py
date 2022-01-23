import os
from gonullu import hafiza,Docker,DockerParams


#TODO: repopath aslinda /var/www/testrepo/pisi-2.0-test olmali, ama uzerinde dusunmeli.
REPOPATH  = "/var/www/html/pisi-2.0"
BASEIMAGE = "ertugerata/pisi-chroot-base"

class DockerIndexer(Docker):
    def __init__(self, fname):
        Docker.__init__(self)
        os.system("cp %s %s/." % (fname, REPOPATH))
        self.params.volume(REPOPATH, '/repo')
        self.set_image_name(BASEIMAGE)
        self.run("cd /repo && pisi index . --skip-signing")

    def add_file(self, fname):
        os.system("cp %s %s/." % (fname, REPOPATH))
        
    def add_files(self, files):
        for f in files:
            self.add_file(f)
    
    def start_index(self):
        self.run("cd /repo && pisi index . --skip-signing")
