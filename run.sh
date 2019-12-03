#!/bin/bash

./youtube-s2rpl.py --channels=900 --videos=500 subs.json | tee ~/tube/$(date +%s)-size_500-playlist.m3u
