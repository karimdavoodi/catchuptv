#!/usr/bin/python3
import os
import sys
import time
import random
from pymongo import MongoClient
from typing import Optional
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse

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


def gen_master_playlist(name, is_live, start):

    if is_live:
        rec = info_db['live'].find_one({'name':name})
    else:
        rec = info_db['vod'].find_one({'name':name})
        
    if not rec:
        raise InternalError('Not found content in DB')

    safe_name = util.uniq_name(name)
    master_play_list = "#EXTM3U\n#EXT-X-VERSION:3\n"
    for bitrate in rec['bitrates']: 
        bw  = bitrate['bandwidth']
        res = bitrate['resolution']
        ty  = "live" if is_live else "vod"
        rnd = random.getrandbits(64)
        master_play_list += (
                f"#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH={bw}," +
                f"RESOLUTION={res!r}\n" +
                f"/v1/cs/offline/play.m3u8?{ty}={safe_name}&bandwidth={bw}&rand={rnd}&start={start}\n" )
    return master_play_list


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/v1/cs/offline/play.m3u8")
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
        
        # Serve Master playlist
        if bandwidth == "":
            master_play_list = gen_master_playlist(name, is_live, start)        
            util.debug(f"Send master play list")
            return Response(content=master_play_list, media_type="application/x-mpegURL")

        # ELSE Serve one playlist
        if not playlist_map.get(rand):
            playlist_map[rand] = int(time.time())
            
        if start == 0 and is_live:
            start = int(time.time())
        hls_time = start
        hls_time += (int(time.time()) - playlist_map[rand])

        collection = util.uniq_name(f"{name}_{bandwidth}")
        segments = seg_db[collection].find(
            {'_id': {
                 '$gt': hls_time,
                 '$lt': hls_time + 30
             }}).limit(5).sort([("_id", 1)])
        playlist = ""
        sequence = -1
        path = f'/v1/cs/offline/segment/{collection}'
        if is_live:
            tm = time.localtime(hls_time)
            path += f"/{tm.tm_year}/{tm.tm_mon}/{tm.tm_mday}/{tm.tm_hour}"
            
        for seg in segments:
            if sequence == -1:
                sequence = seg['sequence']
            segs = "%d.ts" % seg['_id']
            playlist += f"#EXTINF:{seg['duration']},\n"
            playlist += f"{path}/{seg['_id']}.ts\n"
        
        playlist = ("#EXTM3U\n" +
                    "#EXT-X-VERSION:3\n" +
                    "#EXT-X-ALLOW-CACHE:YES\n" +
                    "#EXT-X-MEDIA-SEQUENCE:%d\n" % sequence +
                    "#EXT-X-TARGETDURATION:20\n\n" +
                    playlist)
        if sequence == -1:
            return Response(content=f"Not found segment on col {collection} for time {hls_time}", 
                    status_code=403)

        return Response(content=playlist, media_type="application/x-mpegURL")
    except InternalError as err:
        return Response(content=str(err), status_code=403)
    except:
        util.trace()
        return Response(content="Server error!", status_code=403)

@app.get("/v1/cs/offline/segment/{seg_path:path}")
def live_segment(seg_path:str):
 
    path = f'/data/{seg_path}'
    if os.path.exists(path):
        util.debug(f"Try to senf {path}")
        f = open(path, 'rb')
        return StreamingResponse(f, media_type="video/mp2t")
    else: 
        return Response(content=f"Segment {path} not found!", status_code=403)


