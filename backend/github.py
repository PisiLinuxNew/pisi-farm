import json

"""

"""
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
        self.username = values['username']
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
            if l.find("/files/") > -1:
                pass
            else:
                pkgName = l.split("/")[-2]
                temp.append(pkgName)
        return temp

    def report(self):
        print self.id
        for l in self.modified:
            print "    ",l

class Push:
    def __init__(self,  fname):
        self.fname = fname
        self.content = open(fname).read()
        self.data = json.loads(self.content)
        self.commits = {}
        self.modified()
        self.sender = Sender(self.data['sender'])


    def modified(self):
        commits = self.data['commits']
        for l in commits:
            temp = Commit(l)
            self.commits[temp.id] = temp

    def pprint(self):
        print json.dumps(self.data, indent = 4)

    def html(self):
        commits = "%s <table border=1>" % self.fname
        for k,v in self.commits.items():
            commits += v.html()
        commits += "</table>"
        return commits

if __name__ == "__main__":
    x = Push('20150408040714.txt')
    print x.html()
    #x.pprint()


