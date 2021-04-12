#!/usr/bin/python3
from __future__ import print_function
import os
import sys
import time
import redis
import traceback
from typing import Optional
from fastapi import FastAPI, Response

app = FastAPI()
gb_env = {}
redis_con = None


def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, flush=True, **kwargs)

def lprint():
    eprint(traceback.format_exc())

for var in ['LIVE_CACHE_HOST', 'LIVE_CACHE_PASS']:
    if not os.environ.get(var):
        eprint(f"Please set ENVIRONMENT veriable {var!r}")
        sys.exit(-1)
    gb_env[var] = os.environ[var]

def uniq_name(original_name):
    name = ""
    try:
        for c in original_name:
            if c >= 'a' and c<= 'z':
                name += c.upper()
            elif (c >= 'A' and c<= 'Z') or (c>='0' and c<='9'):
                name += c
            else:
                name += '_'
    except:
        lprint()
    return name

def connect_redis():
    while True:
        try:
            return redis.Redis(host=gb_env['LIVE_CACHE_HOST'], 
                    port=6379, password=gb_env['LIVE_CACHE_PASS'])
        except:
            lprint()
            time.sleep(10)
    time.sleep(3)

redis_con = connect_redis()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/live/play.m3u8")
def live_playlist(channel:str = ""):
    global redis_con
    last = "0"
    channel = uniq_name(channel)
    try:
        last = redis_con.get(f'{channel}-seq-last')
        if not last: 
            return f"Channel {channel!r} not found\n"
    except:
        lprint()
        redis_con = connect_redis()

    last = int(last)
    first = 0 if last < 4 else last-3
    playlist = ("#EXTM3U\n" +
                "#EXT-X-VERSION:3\n" +
                "#EXT-X-ALLOW-CACHE:YES\n" +
                "#EXT-X-MEDIA-SEQUENCE:%d\n" % first +
                "#EXT-X-TARGETDURATION:20\n\n" )
    for i in range(first, last):
        duration = redis_con.get(f'{channel}-{i}-duration').decode()
        playlist += f"#EXTINF:{duration},\n" 
        playlist += f"/live/segment/{channel}-{i}-data.ts\n"

    return Response(content=playlist, media_type="application/x-mpegURL")
 
@app.get("/live/segment/{seg_name}")
def live_segment(seg_name:str):
    data = redis_con.get(seg_name)
    if data:
        return Response(content=data, media_type="video/mp2t")
    else: 
        return "The segment {seg_name!r} not found\n"


