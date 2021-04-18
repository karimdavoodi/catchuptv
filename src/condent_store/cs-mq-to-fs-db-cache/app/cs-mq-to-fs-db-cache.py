#!/usr/bin/python3
import os
import sys
import json
import time
import redis

import util
import rabbitmq
import postgresql

root = '/data'
redis_con = None
gb_env = util.get_env([
    'GB_MQ_HOST', 'GB_MQ_USER', 'GB_MQ_PASS','GB_MQ_SEG_QUEUE', 
    'POSTGRES_HOST', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB',
    'LIVE_CACHE_HOST', 'LIVE_CACHE_PASS'])
    

def connect_redis():
    try:
        return redis.Redis(host=gb_env['LIVE_CACHE_HOST'], 
                port=6379, password=gb_env['LIVE_CACHE_PASS'])
    except:
        util.lprint()

def start_consuming():
    global redis_con
    db = postgresql.PostgreSQL(
            host = gb_env['POSTGRES_HOST'],
            user = gb_env['POSTGRES_USER'],
            passwd = gb_env['POSTGRES_PASSWORD'],
            db = gb_env['POSTGRES_DB'],
            topic = 'segment_info')

    mq = rabbitmq.MQ_direct(
            host = gb_env['GB_MQ_HOST'],        
            user = gb_env['GB_MQ_USER'],        
            passwd = gb_env['GB_MQ_PASS'],   
            queue  = gb_env['GB_MQ_SEG_QUEUE'],   
            ttl = 60000)
    redis_con = connect_redis()
    def consume_mq(ch, method, properties, body):
        global redis_con
        try:
            info_str = body[:512].decode()
            info = json.loads(info_str)
            channel = info['channel']
            resolution = info['resolution']
            bandwidth = info['bandwidth']
            sequence = info['sequence']
            start = info['start']
            duration = info['duration']
        except:
            util.eprint('invalid json:', info_str)
            raise

        channel_uniq = util.uniq_name(channel)
        
        # Send Metadata to DB
        db.insert_row(channel_uniq, f"INSERT INTO {channel_uniq} " + 
                "(channel, sequence, start, duration)" +  
                " VALUES "+
                f"({channel!r},{sequence},{start},{duration})")
        
        # Send to CACHE 
        try:
            redis_con.sadd(f"{channel_uniq}-set", f"{bandwidth}:{resolution}")

            channel_bandwidth = f"{channel_uniq}-{bandwidth}"
            redis_con.set(f"{channel_bandwidth}-seq-last",sequence)
            redis_con.set(f"{channel_bandwidth}-{sequence}-data.ts",body[512:],100)
            redis_con.set(f"{channel_bandwidth}-{sequence}-duration",duration,100)
            util.eprint(f"Send to live cache {channel_uniq!r} seg seq {sequence}")
        except:
            util.lprint()
            redis_con = connect_redis()
            
        # Save in File System
        try:
            tm = time.localtime(int(start))
            seg_path = f"{root}/{channel_uniq}/{tm.tm_year}/{tm.tm_mon}/{tm.tm_mday}/{tm.tm_hour}"
            if not os.path.exists(seg_path):
                os.makedirs(seg_path, exist_ok=True)
            file_path = f"{seg_path}/{start}.ts"
            with open(file_path, 'wb') as f:
                f.write(body[512:])
                util.eprint(f"Write on {file_path}")
        except:
            util.lprint()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    mq.consume(consume_mq)


if __name__ == '__main__':
    while True:
        try:
            util.eprint("Start insert process")
            start_consuming()
        except:
            util.lprint()
        time.sleep(15)
