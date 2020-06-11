#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''sm2p-par.py Justin Hoppensteadt 2019 <justinrocksmadscience@gmail.com
Usage: sm2p.py [options]

Options:
    -C --cache=SECONDS  Seconds of time for cache to expire [default: 300]
    -v --videos=INT     Number of videos to output [default: 500]
    -c --channels=INT   Number of channels to parse per input [default: 1000]

    -b --bitchute=FILE  HTML save of bitchute subscriptions page
    -y --youtube=FILE   Youtube subscription, Download https://www.youtube.com/subscription_manager?action_takeout=1

    -D --debug          Debugging output
    -h --help           Help!

    -o --output=FORMAT Output format m3u, text [default: m3u]

'''

#   -s --state         State file [default: state.yaml]
import requests
import requests_cache
import inspect
import os
import sys
import yaml
import random
import re
# import subprocess
# from time import sleep
# from random import randint

import feedparser
import xmltodict

import asyncio
import aiohttp
from aiohttp import ClientSession

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

from docopt import docopt
# from collections import OrderedDict
from datetime import datetime
from time import mktime
from pprint import pprint, pformat

conf = docopt(__doc__)
tracks = []
channelcount = 0
videocount = 0
#   state = {}

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
    if channelcount > 3:
        dumpentries()


def dumpentries():
    debug("DUMPENTRIES")
    videocount = abs(int(conf['--videos'])) * -1
    s = sorted(
        tracks,
        key=lambda track: track['published_parsed'],
        reverse=False)
    ss = s[videocount:]
    for track in ss:
        try:
            t_id = re.match(r'^\w+(?=:)', track['id'])[0]
        except TypeError as x:
            debug(x)
            t_id = "bitchute"

        t_pub = datetime.strftime(datetime.fromtimestamp(
                mktime(track['published_parsed'])), "%Y-%m-%d %H:%M")
        t_title = re.sub('r[%]+', '', track['title'])
        debug("id: " + track['id'] + " short: " + t_id)
        debug("track: " + track['title'])
        debug("author: " + track['author'])
        debug("published: " + t_pub)
        line = "#EXTINF:0,[{}] {} @{} {}".format(
                track['author'],
                t_title,
                t_id,
                t_pub)
        line = re.sub(r"&amp;", "&", line)
        line = re.sub(r"&quot;", '"', line)
        try:
            if conf['--output']:
                if re.match(r'm3u', conf['--output']):
                    print(line)
                if re.match(r'(m3u|text)', conf['--output']):
                    print(track['link'])
                # if re.match(r'catt|cast', conf['--output']):
                #    print(line)
                #    print(subprocess.call
            else:
                print(line)
                print(track['link'])
        except TypeError:
            print(line)
            print(track['link'])


async def parsechannel(url: str, session: ClientSession, channelName=None, **kwargs):
    global tracks
    #  global state

    try:
        response = await session.request(method="GET", url=url, **kwargs)
        response.raise_for_status()
        text = await response.text()
        channel = feedparser.parse(text)
        for entry in channel['entries']:
            debug(entry)
            if channelName and 'author' not in entry:
                debug(channelName)
                entry['author'] = channelName
            tracks.append(entry)
            debug(entry['title'])
    except BaseException as x:
        debug(x)


async def handlesub(file):
    sub = {}
    #   global state
    counter = 0
    with open(file, "r") as file_h:
        sub = xmltodict.parse(file_h.read())
    # pprint(sub['opml']['body']['outline']['outline'])
    subs = sub['opml']['body']['outline']['outline']
    random.shuffle(subs)
    async with ClientSession() as session:
        tasks = []
        for v in subs:
            # debug(v)
            counter = counter + 1
            if counter <= int(conf['--channels']):
                debug("channel counter: " + str(counter))
                for i, (key, value) in enumerate(v.items()):
                    debug([i, key, value])
                    if key == '@xmlUrl':
                        tasks.append(parsechannel(url=value, session=session))
        await asyncio.gather(*tasks)


def bs_parsechannel(link):
    debug(link)


async def bs_handlesub(file):
    sub = {}
    counter = 0
    with open(file, "r") as file_h:
        sub = BeautifulSoup(file_h.read(), features="lxml")

    subs = sub.body.find_all('a', attrs={'rel': 'author'})
    random.shuffle(subs)
    async with ClientSession() as session:
        tasks = []
        for v in subs:
            counter = counter + 1
            if counter <= int(conf['--channels']):
                debug("channel counter: " + str(counter))
                c = v.get('href')
                cname = None
                try:
                    cname = re.match(r'/channel/(.+)/', c)[1]
                    debug("cname: " + cname)
                except BaseException as x:
                    debug(x)
                link = "https://www.bitchute.com/feeds/rss" + c
                debug(link)
                tasks.append(
                    parsechannel(
                        url=link,
                        channelName=cname,
                        session=session))
        await asyncio.gather(*tasks)


def main():
    debug(["conf", conf])

    #   global state
    #
    #   if conf['--state'] and os.path.exists(conf['--state']):
    #       try:
    #           with open(conf['--state'], 'r') as file_h:
    #               state = yaml.load(file_h)
    #               close(file_h)
    #       except yaml.YAMLError as e:
    #           debug(e)
    #
    #   if not 'youtube' in state:
    #       state['youtube'] = {}
    #   if not 'bitchute' in state:
    #       state['bitchute'] = {}
    #
    #   if conf['--cache']:
    #       requests_cache.install_cache(
    #           'rss',
    #           backend='sqlite',
    #           expire_after=conf['--cache'])

    if conf['--bitchute'] and os.path.exists(conf['--bitchute']):
        try:
            asyncio.run(bs_handlesub(conf['--bitchute']))
        except BaseException as x:
            debug(x)

    if conf['--youtube'] and os.path.exists(conf['--youtube']):
        try:
            asyncio.run(handlesub(conf['--youtube']))
        except BaseException as x:
            debug(x)

    dumpentries()

    #   if conf['--state']:
    #       try:
    #           with open(conf['--state'], 'w') as file_h:
    #               state = yaml.dump(state, file_h)
    #               close(file_h)
    #       except yaml.YAMLError as e:
    #           debug(e)



if __name__ == "__main__":
    main()
