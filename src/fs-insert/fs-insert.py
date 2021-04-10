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
    for c in original_name:
        if c >= 'a' and c<= 'z':
            name += c.upper()
        elif (c >= 'A' and c<= 'Z') or (c>='0' and c<='9'):
            name += c
        else:
            name += '_'
    return name

def send_to_db(table, channel, sequence, start, duration, rtry = False):
    try:
        insert = (f"INSERT INTO {table} " + 
                "(channel, sequence, start, duration)" +  
                " VALUES "+
                f"({channel!r},{sequence},{start},{duration})")
        eprint(f"Try to run {insert}")
        db_cur.execute(insert)
    except psycopg2.InterfaceError:
        lprint()
        db_connection()
        if rtry:
            send_to_db(channel, sequence, start, duration, True)
    except psycopg2.ProgrammingError:
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

def start_consuming():
    # Connect to GB_MQ
    while True:
        try:
            credentials = pika.PlainCredentials(gb_env['GB_MQ_USER'], gb_env['GB_MQ_PASS'])
            parameters = pika.ConnectionParameters(
                    gb_env['GB_MQ_HOST'], 5672, '/', credentials)
            connection = pika.BlockingConnection(parameters)
            channel_seg = connection.channel()
            break
        except:
            lprint()
            time.sleep(10)
    # Connect to LIVE_CACHE
    redis_con = connect_redis()
    def callback(ch, method, properties, body):
        try:
            try:
                info_str = body[:255].decode()
                info = json.loads(info_str)
            except:
                eprint('invalid json:', info_str)
                raise

            channel = info['channel']
            sequence = info['sequence']
            start = info['start']
            duration = info['duration']
            channel_table = uniq_name(channel)
            
            # Send to CACHE Queue
            try:
                redis_con.set(f"{channel}:seq:last",sequence)
                redis_con.set(f"{channel}:{sequence}:data",body[255:],100)
                redis_con.set(f"{channel}:{sequence}:duration",duration,100)
                eprint(f"Send to live cache {channel} seg seq {sequence}")
            except:
                lprint()
                redis_con = connect_redis()
                
            # Send to DB
            send_to_db(channel_table, channel, sequence, start, duration)
            
            # Save in File System
            tm = time.localtime(int(start))
            seg_path = f"{root}/{channel_table}/{tm.tm_year}/{tm.tm_mon}/{tm.tm_mday}/{tm.tm_hour}"
            if not os.path.exists(seg_path):
                os.makedirs(seg_path, exist_ok=True)
            file_path = f"{seg_path}/{start}.ts"
            with open(file_path, 'wb') as f:
                f.write(body[255:])
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
