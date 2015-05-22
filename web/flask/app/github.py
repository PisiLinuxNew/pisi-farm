import json, glob,os
# -*- coding:utf-8 -*-

class Sender:
    def __init__(self, values):
        self.values = values
        v = values
        self.following_url = v['following_url']
        self.events_url = v['events_url']
        self.organizations_url = v['organizations_url']
        self.url = v['url']
        self.gists_url = v['gists_url']
        self.html_url = v['html_url']
        self.subscriptions_url = v['subscriptions_url']
        self.avatar_url = v['avatar_url']
        self.repos_url = v['repos_url']
        self.received_events_url = v['received_events_url']
        self.gravatar_id = v['gravatar_id']
        self.starred_url = v['starred_url']
        if v['site_admin'] == 'false':
            self.site_admin = False
        elif v['site_admin'] == 'true':
            self.site_admin = True
        self.login = v['login']
        self.sendertype = v['type']
        self.id = v['id']
        self.followers_url = v['followers_url']


class User:
    def __init__(self,values):
        try:
            self.username = values['username']
        except:
            pass
        self.name  = values['name']
        self.email = values['email']

    def html(self):
        return '<a href="mailto:%s">%s</a>\n' % (self.email, self.name)

class Commit:
    def __init__(self,values):
        self.committer = User(values['committer'])
        self.added = values['added']
        self.author = User(values['author'])
        self.distinct = values['distinct']
        self.timestamp = values['timestamp']
        self.modified = values['modified']
        self.url = values['url']
        self.message = values['message']
        self.removed = values['removed']
        self.id = values['id']
        self.modifiedPackages = self.modifiedPkg()

    def html(self):
        mes = "%s" % self.message
        author = self.author.html()
        url = "<a href='%s'>%s...%s</a>" % (self.url, self.id[:4], self.id[-4:])
        temp = "<h5>"
        for p in self.modifiedPackages:
            temp += "%s " % p
        temp += "</h5>"
        return "<tr><td><h5>%s</h5></td><td>%s</td><td> %s</td><td> %s</td><td><h5> %s</h5></td></tr>\n" % \
            (self.timestamp, author, url, temp, mes)

    def modifiedPkg(self):
        temp = []
        for l in self.modified:
            filename = l.split("/")[-1].strip()
            if filename in ("index.html","README.md"):
                pass
            elif l.find("/files/") > -1:
                pass
            else:
                a = l.split("/")
                print ">>>",self.id,  l
                if len(a) > 2 :
                    pkgName = l.split("/")[-2]
                    print temp
                    if pkgName not in temp:
                        temp.append(pkgName)
        return temp

    def report(self):
        print self.id
        for l in self.modified:
            print "    ",l

    def db(self):
        if len(self.modifiedPackages) > 0:
            return {"id" : self.id, "url" : self.url, "modified" : self.modifiedPackages}
        return None


class Push:
    def __init__(self,  fname):
        self.fname = fname
        self.content = open(fname).read()
        self.data = json.loads(self.content)
        self.commits = {}
        self.modified()
        self.ref = self.data['ref'].split("/")[-1]
        self.sender = Sender(self.data['sender'])

    def db(self):
        temp = {}
        for c, com in self.commits.items():
            d = com.db()
            if d != None:
                temp[d["id"]] = d
        return temp

    def modified(self):
        if 'commits' in self.data.keys():
            commits = self.data['commits']
            for l in commits:
                temp = Commit(l)
                self.commits[temp.id] = temp

    def pprint(self):
        print json.dumps(self.data, indent = 4)

    def html(self):
        commits = "Tarih : %s   Branch : %s <table border=1>" % (self.fname, self.ref)
        for k,v in self.commits.items():
            commits += v.html()
        commits += "</table>"
        return commits.encode("utf-8")

import sys
if __name__ == "__main__":
    indir = sys.argv[1]
    outfile = sys.argv[2]
    os.chdir(indir)
    out = open(outfile,"w")
    out.write("<html>")
    files = sorted(glob.glob("*.txt"), reverse=True)
    for f in files:
        print f
        x = Push(f)
        page = x.html()
        if len(page) > 45:
            out.write(page)
    out.write("</html>")
    out.close()
    #x.pprint()


