#!/bin/bash

set -x

VIDEOS=${1:-250}
DATE=$(date +%s)
FILE=~/tube/$DATE-size_$VIDEOS-playlist.m3u

if [ ! -d ~/tube ] ; then
    mkdir ~/tube
fi

#./sm2p-par.py --channels=1100 --videos=$VIDEOS -b bitchute.html -y subs.json | tr -d '%' | tee $FILE
./sm2p-par.py --channels=1100 --videos=$VIDEOS -y subs.json | tr -d '%' | tee $FILE
castadd $FILE

cd ~/tube
ln -svf $FILE ./latest.m3u
