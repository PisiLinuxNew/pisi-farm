#!/bin/bash
/usr/bin/uwsgi --socket 127.0.0.1:3031 --py-autoreload 1 --wsgi-file farm.py --callable app --processes 4 --threads 2 --stats 127.0.0.1:9191 --logto /home/uygulama/farm/farm_hata.log
