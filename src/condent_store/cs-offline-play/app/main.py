#!/usr/bin/python3
import os
import sys
import time
import random
from typing import Optional
from fastapi import FastAPI, Response

import util
import postgresql

app = FastAPI()

gb_env = util.get_env(['LIVE_CACHE_HOST', 'LIVE_CACHE_PASS'])

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/live/play.m3u8")
def live_playlist(
        channel: str, 
        start: float , 
        bandwidth : Optional[str] = "", 
        radio_idx : Optional[int] = 0 
        ):

    channel = util.uniq_name(channel)

    if radio_idx == 0:
        radio_idx = random.getrandbits(64)

    if bandwidth == "":
        # Serve Master playlist
        master_play_list = "#EXTM3U\n#EXT-X-VERSION:3\n"
        for item in redis_con.smembers(f'{channel}-set'): 
            tok = str(item.decode()).split(':')
            bandwidth = tok[0]
            resolution = tok[1]
            master_play_list += (f'#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH={bandwidth},'+
                    f'RESOLUTION={resolution!r}\n' +
                    f'/live/play.m3u8?channel={channel}&bandwidth={bandwidth}\n' )
        return Response(content=master_play_list, media_type="application/x-mpegURL")
    else:
        # Serve one playlist
        channel_table = util.uniq_name(f"{channel}_{bandwidth}")
        last = redis_con.get(f'{channel_table}-seq-last')
        if not last: 
            return f"Channel {channel!r} not found(2)\n"
        last = int(last)
        first = 0 if last < 4 else last-3
        playlist = ("#EXTM3U\n" +
                    "#EXT-X-VERSION:3\n" +
                    "#EXT-X-ALLOW-CACHE:YES\n" +
                    "#EXT-X-MEDIA-SEQUENCE:%d\n" % first +
                    "#EXT-X-TARGETDURATION:20\n\n" )
        for i in range(first, last):
            duration = str(redis_con.get(f'{channel_table}-{i}-duration').decode())
            playlist += f"#EXTINF:{duration},\n" 
            playlist += f"/live/segment/{channel_table}-{i}-data.ts\n"

        return Response(content=playlist, media_type="application/x-mpegURL")
 
@app.get("/live/segment/{seg_name}")
def live_segment(seg_name:str):
    data = redis_con.get(seg_name)
    if data:
        return Response(content=data, media_type="video/mp2t")
    else: 
        return "The segment {seg_name!r} not found\n"


