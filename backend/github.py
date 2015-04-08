import json

class Push:
    def __init__(self,  fname):
        self.content = open(fname).read()
        self.data = json.loads(self.content)



    def pprint(self):
        print json.dumps(self.data, indent = 4)

    def html(self):
        pass

if __name__ == "__main__":
    x = Push('20150408040714.txt')
    x.pprint()


