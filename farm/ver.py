
class Subversion:
    def __init__(self, version_str):
        self.ayirac = "-,|".split(",")
        self.version = version_str
        self.major = None
        self.minor = None
        self.parse()

    def __repr__(self):
        if self.minor is not None:
            return "%d %s" % (self.major, self.minor)
        else:
            return "%d" % self.major
        
    def __eq__(self, subver):
        if (subver.major == self.major) and (subver.minor == self.minor):
            return True
        return False

    def __lt__(self, subver):
        if (self.major < subver.major):
            return True
        elif (self.major > subver.major):
            return False
        if (self.minor < subver.minor):
            return True
        return False
    
    def __gt__(self, subver):
        if (self.major > subver.major):
            return True
        elif (self.major < subver.major):
            return False
        if (self.minor > subver.minor):
            return True
        return False
    
    def parse(self):
        parcalar = None
        for ayirac in self.ayirac:
            if self.version.find(ayirac) > -1:
                parcalar = self.version.split(ayirac)
                self.major = int(parcalar[0])
                self.minor = parcalar[1]
                break

        if parcalar is None: # ayirac bulamamis 1a gibi birsey gelmis ise
            if self.version.isdigit():
                self.major = int(self.version)
            else:
                for i in range(len(self.version)):
                    if self.version[:-1 * i].isdigit() is True:
                        self.major = int(self.version[:-1 * i])
                        self.minor =  self.version[i+1:]
                        break
                
        if self.major is None:
            print("alt versiyon stringi problemli :", self.version)
            print("repo.py dosyasinda Subversion sinifi icinde duzeltme gerek")
            raise ValueError

class Version:
    def __init__(self, version_str, ayirac = "."):
        self.version = version_str
        self.ayirac = ayirac
        self.parcalar = {}
        self.parse()

    def parse(self):
        parcalar = self.version.split(self.ayirac)
        for p in enumerate(parcalar):
            self.parcalar[p[0]] = Subversion(p[1])
            

    def __eq__(self, other):
        if self.version == other.version:
            return True
        return False

    def __gt__(self, other):
        if self.version == other.version:
            return None
        return not(self.__lt__(other))
    
    def __lt__(self, other):
        if self.version == other.version:
            return None
        parca = 0
        mylen = len(self.parcalar.keys())
        digerlen = len(other.parcalar.keys())
        if digerlen > mylen:
            parca = mylen
        else:
            parca = digerlen
        for i in range(parca):
            if self.parcalar[i] < other.parcalar[i]:
                return True
            elif self.parcalar[i] > other.parcalar[i]:
                return False
        if digerlen > mylen:
            return True
        elif digerlen < mylen:
            return False
        
        return None
                

if __name__ == "__main__":
    s1 = Version("1.21.12a")
    s2 = Version("1.21")
    print(s2 < s1)
