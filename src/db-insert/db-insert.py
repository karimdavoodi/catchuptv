#!/usr/bin/python3
from __future__ import print_function
import os
import sys
import pika
import json
import time
import psycopg2

gb_env = {}
db_conn = None
db_cur = None
  

def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, flush=True, **kwargs)

for var in ['GB_MQ_HOST', 'GB_MQ_USER', 'GB_MQ_PASS', 
            'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB', 'POSTGRES_HOST']:
    if not os.environ.get(var):
        eprint(f"Please set ENVIRONMENT veriable {var!r}")
        sys.exit(-1)
    gb_env[var] = os.environ[var]
   
mq_queue = 'epg' if 'epg' in os.environ['POSTGRES_HOST'] else 'seg_info'
table_name = mq_queue

if table_name == 'epg':
    table_struct = ( f"create table epg ("+
                "ID              SERIAL PRIMARY KEY," +
                "channel         varchar(127)," +
                "channelSid      int," +
                "programName     varchar(255)," +
                "programStart    real," +
                "programEnd      real" +
                ")" )
elif table_name == "seg_info":
    table_struct = ( f"create table seg_info ("+
                "ID        SERIAL PRIMARY KEY," +
                "channel   varchar(127)," +
                "start     real," +
                "duration  real" +
                ")" )
else:
    eprint(f"Table name is invalid: {table_name}")
    sys.exit(-1)
    
# Connect to PostgreSQL
def db_connection():
    global gb_env, db_conn, db_cur, table_name
    
    db_conn = psycopg2.connect(
            host = gb_env['POSTGRES_HOST'],
            database = gb_env['POSTGRES_DB'],
            user = gb_env['POSTGRES_USER'],
            password = gb_env['POSTGRES_PASSWORD'])
    db_conn.autocommit = True

    db_cur = db_conn.cursor()
    try:
        db_cur.execute(f"select * from {table_name}")
        #rows = db_cur.fetchall()
        #for r in rows:
        #    eprint(str(r))

    except Exception as err:
        eprint(str(err))
        eprint(f"Try to create table: {table_struct}")
        db_cur.execute(table_struct)

    eprint(f"Connected to PostgreSQL host {gb_env['POSTGRES_HOST']}, db {gb_env['POSTGRES_DB']}")

def start():
    credentials = pika.PlainCredentials(gb_env['GB_MQ_USER'], gb_env['GB_MQ_PASS'])
    parameters = pika.ConnectionParameters(
            gb_env['GB_MQ_HOST'], 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(
            queue=mq_queue, 
            passive=False, 
            durable=True,  
            exclusive=False, 
            auto_delete=False)

    def callback(ch, method, properties, body):
        global db_cur
        try:
            if not db_cur:
                eprint('invalid db cursor')
                return
            rec = json.loads(body.decode())
            if table_name == "epg":
                channel      = rec['channel'] 
                channelSid   = rec['channelSid'] 
                programName  = rec['programName'] 
                programStart = rec['programStart'] 
                programEnd   = rec['programEnd'] 
                insert = ( 
                        f"INSERT INTO {table_name} " + 
                        "(channel, channelSid, programName, programStart, programEnd)" +  
                        " VALUES "+
                        f"({channel!r},{channelSid},{programName!r},{programStart},{programEnd})"
                        )
            else:
                # TODO: seperate channels table for spped up query time
                channel      = rec['start'] 
                channelSid   = rec['duration'] 
                programName  = rec['channel'] 
                insert = ( 
                        f"INSERT INTO {table_name} " + 
                        "(channel, start, duration)" +  
                        " VALUES "+
                        f"({channel!r},{start},{duration})"
                        )

            eprint(f"Try to run {insert}")
            db_cur.execute(insert)
        except Exception as err:
            eprint(f"Error(1): ", str(err))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    eprint(f"Wait for MQ on host {gb_env['GB_MQ_HOST']}, queue {mq_queue}")
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=mq_queue, on_message_callback=callback)
    channel.start_consuming()

if __name__ == '__main__':
    while True:
        try:
            eprint("Start insert process")
            db_connection()
            start()
        except Exception as err:
            eprint('Error(2):', str(err))
        time.sleep(15)
