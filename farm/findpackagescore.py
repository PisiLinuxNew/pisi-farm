#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# find which packages were not compiled in farm
# usage: scriptname  svnindex  pisiindex
#


import os
import sys

import urllib2
import bz2
import lzma

import piksemel

pisirepouri = "https://ciftlik.pisilinux.org/2.0-Beta.1/pisi-index.xml.xz"
#svnrepouri  = "https://github.com/ertugerata/main/raw/master/pisi-index.xml.xz"
svnrepouri  = "https://github.com/ertugerata/core/raw/master/pisi-index.xml.xz"
def getIndex(uri):
    try:
        if "://" in uri:
            rawdata = urllib2.urlopen(uri).read()
        else:
            rawdata = open(uri, "r").read()
    except IOError:
        print "could not fetch %s" % uri
        return None

    if uri.endswith("bz2"):
        data = bz2.decompress(rawdata)
    elif uri.endswith("xz") or uri.endswith("lzma"):
        data = lzma.decompress(rawdata)
    else:
        data = rawdata

    return data

def parseRepo(repoURI):
    pkgdict = {}

    rawData = getIndex(repoURI)
    doc = piksemel.parseString(rawData)
    hasSpecFile = doc.getTag("SpecFile")

    if hasSpecFile:
        for parent in doc.tags("SpecFile"):
            pkgname = parent.getTag("Source").getTagData("Name")
            srcname = pkgname

            partof = parent.getTag("Source").getTagData("PartOf")

            lastRelease = parent.getTag("History").tags("Update").next()
            release = lastRelease.getAttribute("release")

            pkgdict[srcname] = [partof, release]
    else:
        for parent in doc.tags("Package"):
            pkgname = parent.getTagData("Name")
            srcname = parent.getTag("Source").getTagData("Name")

            partof = parent.getTagData("PartOf")

            lastRelease = parent.getTag("History").tags("Update").next()
            release = lastRelease.getAttribute("release")

            pkgdict[srcname] = [partof, release]

    return pkgdict

if __name__ == "__main__":
    pkgmissing = []
    pkgdifferent = []

    if len(sys.argv) > 1:
        svnrepouri = sys.argv[1]

    if len(sys.argv) > 2:
        pisirepouri = sys.argv[2]

    print
    print "* working on %s" % svnrepouri
    svnrepo = parseRepo(svnrepouri)

    print "* working on %s" % pisirepouri
    pisirepo = parseRepo(pisirepouri)

    pkglist = svnrepo.keys()
    pkglist.sort()

    for i in pkglist:
        if not i in pisirepo:
            partof = svnrepo[i][0]
            pkgmissing.append("%s/%s" % (partof.replace(".", "/"), i))

        elif svnrepo[i][1] != pisirepo[i][1]:
            partof = svnrepo[i][0]
            pkgdifferent.append("%s/%s" % (partof.replace(".", "/"), i))

    pkgmissing.sort()
    pkgdifferent.sort()

    if len(pkgmissing):
        print
        print "* Packages missing in %s" % pisirepouri
        for p in pkgmissing:
            print "  %s" % p
    file = open('findcore.txt','w')
    if len(pkgdifferent):
        print
        print "* Packages that needs compiling"
        for p in pkgdifferent:
            i = p.split("/")[-1]
            sonuc = "  %s  (%s > %s)\n" % (p, svnrepo[i][1], pisirepo[i][1])
            file.write(sonuc)
            print sonuc

    print

 
