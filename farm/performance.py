class PackageLog:
    def __init__(self, pname):
        self.name = pname
        self.err = None
        self.log = None

class Volunteer:
    def __init__(self, email):
        self.email = email
        self.load = 0
        self.memory = 0
        self.packages = {}

    def add_package(self, pkg):
        self.packages[pkg.name] = pkg

    def report(self):
        pkg = {}
        for p in self.packages:
            pkg[p.name] = { "log": p.log, "err": p.err }
        return { "email": self.email , "load": self.load, "memory": self.memory, "pkg": pkg }


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

    def report(self):
        temp = {}
        for v in self.volunteers.items():
            temp[vl.email] = v.report()
