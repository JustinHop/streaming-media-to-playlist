#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''youtube-s2rpl Justin Hoppensteadt 2019 <justinrocksmadscience@gmail.com
Usage: youtube-s2rpl [options] FILE

Options:
    -D --debug          Debugging output
    -v --videos=INT     Number of videos to output [default: 500]
    -c --channels=INT   Number of channels to parse [default: 1000]
    -s --starttime      Oldest video to display
    -r --resume         Resume see/unseen
    -h --help           Help!

Arguments:
    FILE            Youtube subs xml file from https://www.youtube.com/subscription_manager?action_takeout=1
'''

import requests
import requests_cache
import inspect
import os
import sys
import yaml
import random
import re

import feedparser
import xmltodict

from docopt import docopt
# from collections import OrderedDict
from pprint import pprint, pformat

conf = docopt(__doc__)
tracks = []
channelcount = 0
videocount = 0

requests_cache.install_cache(
    'rss',
    backend='sqlite',
    expire_after=3600)


try:
    basestring
except NameError:  # python3
    basestring = str


def debug(message):
    if conf['--debug']:
        print(inspect.stack()[1].function, ":", message, file=sys.stderr)


def handlechannel(url):
    global channelcount
    global tracks
    channelcount = channelcount + 1
    debug("channelcount: " + str(channelcount))
    response = requests.get(url)
    text = response.text
    debug(["response.text", text])
    channel = xmltodict.parse(text)
    # debug(pformat(channel['feed']))
    for i, (key, value) in enumerate(channel['feed'].items()):
        # print("channel['feed'].items():", i, key, value)
        if key == "link":
            for ii, (kkey, vvalue) in enumerate(value):
                # print("value.items():", ii, kkey, vvalue, value[ii])
                if vvalue == "@href":
                    # print("value.items()[@href]:", value[ii][vvalue])
                    pass
        elif key == "entry":
            for ii, entries in enumerate(value):
                tracks.append(entries)
                try:
                    print("ii, entrys:", ii, entries)
                except TypeError:
                    pass
                for entry in entries:
                    try:
                        debug(["entry, entries[entry]:", entry, entries[entry]])
                    except TypeError as x:
                        debug(x)
                    # print(yaml.dump(entries[entry]))
                    # tracks.append(entry)
    if channelcount > 3:
        dumpentries()


def dumpentries():
    debug("DUMPENTRIES")
    videocount = abs(int(conf['--videos'])) * -1
    # pprint(tracks)
    # debug("DUMPENTRIES raw tracks")
    for track in tracks:
        # debug(track['title'])
        # debug(track['published'])
        pass
    s = sorted(tracks, key=lambda track: track['published'], reverse=False)
    ss = s[videocount:]
    # ss.reverse()
    print("#EXTM3U")
    for track in ss:
        # print(track['title'], track['published'], track['published_parsed'])
        t_id = re.match(r'^\w+(?=:)', track['id'])[0]
        t_pub = re.match(r'^.*(?=T)', track['published'])[0]
        debug("id: " + track['id'] + " short: " + t_id)
        debug("track: " + track['title'])
        debug("author: " + track['author'])
        debug("published: " + t_pub)
        print("#EXTINF:0,[{}] {} @{} {}".format(
                track['author'],
                track['title'],
                t_id,
                t_pub))
        print(track['link'])
    # for track in tracks:
    #     print("Dumping: ", track)


def parsechannel(url):
    global tracks

    try:
        response = requests.get(url)
        text = response.text
        # debug(["response.text", text])
        channel = feedparser.parse(text)
        for entry in channel['entries']:
            tracks.append(entry)
            # debug(entry['title'])
            # debug(entry['published'])
    except BaseException as x:
        debug(x)


def handlesub(file):
    sub = {}
    counter = 0
    with open(file, "r") as file_h:
        sub = xmltodict.parse(file_h.read())
    # pprint(sub['opml']['body']['outline']['outline'])
    for v in sub['opml']['body']['outline']['outline']:
        # debug(v)
        counter = counter + 1
        if counter <= int(conf['--channels']):
            debug("channel counter: " + str(counter))
            for i, (key, value) in enumerate(v.items()):
                debug([i, key, value])
                if key == '@xmlUrl':
                    parsechannel(value)


def main():
    debug(["conf", conf])
    if conf['FILE'] and os.path.exists(conf['FILE']):
        handlesub(conf['FILE'])
        dumpentries()


if __name__ == "__main__":
    main()
