#!/usr/bin/python3
import os
import sys
import time
import random
from pymongo import MongoClient
from typing import Optional
from fastapi import FastAPI, Response

import util

app = FastAPI()

playlist_map:dict = {}    

gb_env = util.get_env([
    'CS_DB_INFO_URL',
    'CS_DB_INFO_DB',
    'CS_DB_SEG_URL',
    'CS_DB_SEG_DB'
    ])
mongo_client_info = MongoClient(gb_env['CS_DB_INFO_URL']) 
info_db = mongo_client_info[gb_env['CS_DB_INFO_DB']]

mongo_client_seg = MongoClient(gb_env['CS_DB_SEG_URL']) 
seg_db = mongo_client_seg[gb_env['CS_DB_SEG_DB']]

class InternalError(Exception):
    pass


def gen_master_playlist(name, safe_name, is_live, start):

    if is_live:
        rec = info_db['live'].find_one({'name':name})
    else:
        rec = info_db['vod'].find_one({'name':name})
        
    if not rec:
        raise InternalError('Not found content in DB')

    master_play_list = "#EXTM3U\n#EXT-X-VERSION:3\n"
    for bitrate in rec['bitrates']: 
        bw  = bitrate['bandwidth']
        res = bitrate['resolution']
        ty  = "live" if is_live else "vod"
        rnd = random.getrandbits(64)
        master_play_list += (
                f"#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH={bw}," +
                f"RESOLUTION={res!r}\n" +
                f"/live/play.m3u8?{ty}={safe_name}&bandwidth={bw}&rand={rnd}&start={start}\n" )
    return master_play_list


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/offline/play.m3u8")
def live_playlist(
        live      : Optional[str] = "", 
        vod       : Optional[str] = "", 
        start     : Optional[int] = 0 , 
        bandwidth : Optional[str] = "", 
        rand      : Optional[int] = 0 
        ):
    try:
        is_live = True if live != "" else False
        name = live if live != "" else vod
        if name == "": 
            raise InternalError("Require 'live' or 'vod' parameter")
        safe_name = util.uniq_name(name)
        
        # Serve Master playlist
        if bandwidth == "":
            master_play_list = gen_master_playlist(name, safe_name, is_live, start)        
            return Response(content=master_play_list, media_type="application/x-mpegURL")

        # ELSE Serve one playlist
        if not playlist_map.get(rand):
            playlist_map[rand] = {
                    "base_time": int(time.time()),
            }

        if start == 0 and is_live:
            start = int(time.time())
        hls_time = start
        hls_time += (int(time.time()) - playlist_map[rand])

        collection = f"{safe_name}_{bandwidth}"
        segments = seg_db[collection].find(
            {'_id': {
                 '$gt': hls_time,
                 '$lt': hls_time + 30
             }}).limit(5).sort([("_id", 1)])
        playlist = ""
        sequence = -1
        path = f'/offline/segment/{collection}'
        if is_live:
            tm = time.localtime(hls_time)
            path += f"/{tm.tm_year}/{tm.tm_mon}/{tm.tm_mday}/{tm.tm_hour}"
            
        for seg in segments:
            if sequence == -1:
                sequence = seq['sequence']
            segs = "%d.ts" % seg['_id']
            playlist += "#EXTINF:{seg['duration']},\n"
            playlist += "{path}/{seg['_id']}.ts"

        playlist = ("#EXTM3U\n" +
                    "#EXT-X-VERSION:3\n" +
                    "#EXT-X-ALLOW-CACHE:YES\n" +
                    "#EXT-X-MEDIA-SEQUENCE:%d\n" % sequesnce +
                    "#EXT-X-TARGETDURATION:20\n\n" +
                    playlist)

        return Response(content=playlist, media_type="application/x-mpegURL")
    except InternalError as err:
        return Response(content=str(err), status_code=403)
    except:
        util.trace()
        return Response(content="Server error!", status_code=403)

@app.get("/live/segment/{seg_path:path}")
def live_segment(seg_path:str):

    path = '/data/{seg_path}'
    if os.path.exists(path):
        with open(path) as f:
            return Response(content=f, media_type="video/mp2t")
    else: 
        return Response(content=f"Segment {path} not found!", status_code=403)


