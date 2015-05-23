#!/bin/bash
cd /root
pisi bi --ignore-safety -y $1 1>$2-$1.log 2>$2-$1.err
STAT=$?
for s in *.pisi
do
  mv $s $2-$s
done
echo $STAT >  $1.bitti
