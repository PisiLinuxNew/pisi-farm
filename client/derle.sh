#!/bin/bash
service dbus start
pisi ur 
cd /root
pisi bi --ignore-safety -y $3 1>$1-$2-$3.log 2>$1-$2-$3.err
STAT=$?
for s in *.pisi
do
  mv $s $1-$2-$s
done
echo $STAT >  $3.bitti
