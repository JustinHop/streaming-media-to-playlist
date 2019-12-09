#!/bin/bash

./sm2p-par.py --channels=1000 --videos=555 -b bitchute.html -y subs.json | tr -d '%' | tee ~/tube/$(date +%s)-size_555-playlist.m3u
