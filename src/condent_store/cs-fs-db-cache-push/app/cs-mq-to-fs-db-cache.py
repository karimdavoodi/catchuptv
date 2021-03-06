#!/usr/bin/python3
import os
import sys
import json
import time
import redis
from pymongo import MongoClient

import util
import rabbitmq

root = '/data'
gb_env = util.get_env([
    'CS_GB_MQ_SERVICE_HOST',
    'GB_MQ_USER', 
    'GB_MQ_PASS',
    'GB_MQ_SEG_QUEUE', 
    'CS_DB_SEG_URL',
    'CS_DB_SEG_DB',
    'CS_LIVE_CACHE_SERVICE_HOST', 
    'LIVE_CACHE_PASS'])
    

def start_consuming():
    mongo_client = MongoClient(gb_env['CS_DB_SEG_URL']) 
    db = mongo_client[gb_env['CS_DB_SEG_DB']]

    mq = rabbitmq.MQ_direct(
            host = gb_env['CS_GB_MQ_SERVICE_HOST'],        
            user = gb_env['GB_MQ_USER'],        
            passwd = gb_env['GB_MQ_PASS'],   
            queue  = gb_env['GB_MQ_SEG_QUEUE'],   
            ttl = 60000)

    redis_con = redis.Redis(
            host=gb_env['CS_LIVE_CACHE_SERVICE_HOST'], 
            port=6379, 
            password=gb_env['LIVE_CACHE_PASS'])
    def consume_mq(ch, method, properties, body):
        is_channel = False
        try:
            info_str = body[:512].decode()
            info = json.loads(info_str)
            if info.get('channel'):
                channel = info['channel']
                is_channel = True
            elif info.get('file'):
                channel = info['file']

            resolution = info['resolution']
            bandwidth = info['bandwidth']
            sequence = info['sequence']
            start = info['start']
            duration = info['duration']
        except:
            util.error('invalid json:' + info_str)
            raise

        channel_table = util.uniq_name(f"{channel}_{bandwidth}")
        channel_uniq = util.uniq_name(channel)
        
        # Send Metadata to DB
        try:
            rec = {
                    "_id": start,
                    "sequence": sequence,
                    "duration": duration
                    }
            db[channel_table].insert_one(rec)
            util.debug(f"insert on DB col: {channel_table} data: {rec}")
        except:
            util.trace()
        
        if is_channel:
            # Send to CACHE 
            try:
                redis_con.sadd(f"all-channels-set", channel)
                redis_con.sadd(f"{channel_uniq}-set", f"{bandwidth}:{resolution}")

                redis_con.set(f"{channel_table}-seq-last",sequence)
                redis_con.set(f"{channel_table}-{sequence}-data.ts",body[512:],100)
                redis_con.set(f"{channel_table}-{sequence}-duration",duration,100)
                util.debug(f"Send to live cache {channel_table!r} seg seq {sequence}")
            except:
                util.trace()
            
        # Save in File System
        try:
            seg_path = f"{root}/{channel_table}"
            if is_channel:
                tm = time.localtime(int(start))
                seg_path += f"/{tm.tm_year}/{tm.tm_mon}/{tm.tm_mday}/{tm.tm_hour}"
            if not os.path.exists(seg_path):
                os.makedirs(seg_path, exist_ok=True)
            file_path = f"{seg_path}/{start}.ts"
            with open(file_path, 'wb') as f:
                f.write(body[512:])
                util.debug(f"Write on {file_path}")
        except:
            util.trace()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    mq.consume(consume_mq)


if __name__ == '__main__':
    while True:
        try:
            util.info("Start insert process")
            start_consuming()
        except:
            util.trace()
        time.sleep(15)
