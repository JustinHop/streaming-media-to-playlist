#!/bin/bash

./sm2p.py --channels=900 --videos=555 -b bitchute.html -y subs.json | tr -d '%' | tee ~/tube/$(date +%s)-size_555-playlist.m3u
