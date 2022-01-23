class PackageLog:
    def __init__(self, pname):
        self.name = pname
        self.err = None
        self.log = None
        self.log = None

class Volunteer:
    def __init__(self, email):
        self.email = email
        self.load = 0
        self.memory = 0
        self.packages = {}

    def add_package(self, pkg):
        self.packages[pkg.name] = pkg


class Performance:
    def __init__(self):
        self.volunteers = {}

    def add_volunteer(self, vl):
        self.volunteers[vl.email] = vl


    def total_memory(self):
        t = 0
        for h in self.helpers.values():
            t += h.memory
        return t

    def total_load(self):
        t = 0
        for h in self.helpers.values():
            t += h.load
        return t

