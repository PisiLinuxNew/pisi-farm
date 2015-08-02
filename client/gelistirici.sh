#!/bin/bash
# birinci paket adi,
# ikinci pspec adresi
service dbus start
pisi ur
cd /root
pisi bi --ignore-safety -y $2 1>$1.log 2>$1.err
STAT=$?
echo $STAT >  $1.bitti
