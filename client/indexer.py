from gonullu import hafiza,Docker,DockerParams

REPOPATH  = "/var/www/html/pisi-2.0"
BASEIMAGE = "ertugerata/pisi-chroot-base"

class DockerIndexer(Docker):
    def __init__(self):
        Docker.__init__(self)
        self.params.volume(REPOPATH, '/repo')
        self.set_image_name(BASEIMAGE)
        self.run("cd %s && pisi index . --skip-signing")

index = DockerIndexer()
