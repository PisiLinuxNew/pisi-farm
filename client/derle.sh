#!/bin/bash
cd /root
pisi bi --ignore-safety -y $1 1>$1.log 2>$1.err
touch $1.bitti
