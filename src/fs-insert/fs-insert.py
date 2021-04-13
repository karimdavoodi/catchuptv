#!/usr/bin/python3
from __future__ import print_function
import os
import sys
import pika
import json
import time
import redis
import psycopg2
import traceback

root = '/data'
gb_env = {}

def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, flush=True, **kwargs)

def lprint():
    eprint(traceback.format_exc())

for var in ['GB_MQ_HOST', 'GB_MQ_USER', 'GB_MQ_PASS','GB_MQ_SEG_QUEUE', 
        'POSTGRES_HOST', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB',
        'LIVE_CACHE_HOST', 'LIVE_CACHE_PASS']:
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

def send_to_db(table, channel, sequence, start, duration, rtry = False):
    try:
        insert = (f"INSERT INTO {table} " + 
                "(channel, sequence, start, duration)" +  
                " VALUES "+
                f"({channel!r},{sequence},{start},{duration})")
        eprint(f"Try to run {insert}")
        db_cur.execute(insert)
    except psycopg2.InterfaceError:  # Connection problem!
        lprint()
        db_connection()
        if rtry:
            send_to_db(channel, sequence, start, duration, True)
    except psycopg2.ProgrammingError: # Table not exists (maybe)
        lprint()
        table_struct = ( f"create table {table} ("+
                "ID        SERIAL PRIMARY KEY," +
                "channel   varchar(127)," +
                "sequence  int," +
                "start     real," +
                "duration  real)" )
        db_cur.execute(table_struct)
        if rtry:
            send_to_db(channel, sequence, start, duration, True)
    except:
        lprint()
    eprint(f"Wrote to DB seq start {start}")

def connect_redis():
    while True:
        try:
            return redis.Redis(host=gb_env['LIVE_CACHE_HOST'], 
                    port=6379, password=gb_env['LIVE_CACHE_PASS'])
        except:
            lprint()
            time.sleep(10)
def connect_rabbitmq():
    while True:
        try:
            credentials = pika.PlainCredentials(gb_env['GB_MQ_USER'], gb_env['GB_MQ_PASS'])
            parameters = pika.ConnectionParameters(
                    gb_env['GB_MQ_HOST'], 5672, '/', credentials)
            return pika.BlockingConnection(parameters)
        except:
            lprint()
            time.sleep(10)

redis_con = None
def start_consuming():
    redis_con = connect_redis()
    rabbitmq_con = connect_rabbitmq()
    channel_seg = rabbitmq_con.channel()
    def callback(ch, method, properties, body):
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
            eprint('invalid json:', info_str)
            raise

        channel_uniq = uniq_name(channel)
        
        # Send Metadata to DB
        send_to_db(channel_uniq, channel, sequence, start, duration)
        
        # Send to CACHE 
        try:
            redis_con.sadd(f"{channel_uniq}-set", f"{bandwidth:resolution}")

            channel_bandwidth = f"{channel_uniq}-{bandwidth}"
            redis_con.set(f"{channel_bandwidth}-seq-last",sequence)
            redis_con.set(f"{channel_bandwidth}-{sequence}-data.ts",body[512:],100)
            redis_con.set(f"{channel_bandwidth}-{sequence}-duration",duration,100)
            eprint(f"Send to live cache {channel_uniq!r} seg seq {sequence}")
        except:
            lprint()
            redis_con = connect_redis() #maybe disconnected
            
        # Save in File System
        try:
            tm = time.localtime(int(start))
            seg_path = f"{root}/{channel_uniq}/{tm.tm_year}/{tm.tm_mon}/{tm.tm_mday}/{tm.tm_hour}"
            if not os.path.exists(seg_path):
                os.makedirs(seg_path, exist_ok=True)
            file_path = f"{seg_path}/{start}.ts"
            with open(file_path, 'wb') as f:
                f.write(body[512:])
                eprint(f"Write on {file_path}")
        except:
            lprint()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel_seg.basic_qos(prefetch_count=1)
    channel_seg.basic_consume(queue=gb_env['GB_MQ_SEG_QUEUE'], on_message_callback=callback)
    channel_seg.start_consuming()

def db_connection():
    global gb_env, db_conn, db_cur
    eprint(f"Try to Connect to DB on {gb_env['POSTGRES_HOST']}, db {gb_env['POSTGRES_DB']}")
    while True: 
        try:
            eprint(f"Try to Connect to DB on {gb_env['POSTGRES_HOST']}, db {gb_env['POSTGRES_DB']}")
            db_conn = psycopg2.connect(
                host = gb_env['POSTGRES_HOST'],
                database = gb_env['POSTGRES_DB'],
                user = gb_env['POSTGRES_USER'],
                password = gb_env['POSTGRES_PASSWORD'])
            db_conn.autocommit = True
            db_cur = db_conn.cursor()
            break
        except:
            lprint()
            time.sleep(10)
    eprint(f"Connect to PostgreSQL host {gb_env['POSTGRES_HOST']}, db {gb_env['POSTGRES_DB']}")

if __name__ == '__main__':
    while True:
        try:
            eprint("Start insert process")
            db_connection()
            start_consuming()
        except:
            lprint()
        time.sleep(15)
