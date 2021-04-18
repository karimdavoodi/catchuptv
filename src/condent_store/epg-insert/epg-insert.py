#!/usr/bin/python3
from __future__ import print_function
import os
import sys
import pika
import json
import time
import psycopg2
import traceback

gb_env = {}
db_conn = None
db_cur = None
  

def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, flush=True, **kwargs)
def lprint():
    eprint(traceback.format_exc())

for var in ['GB_MQ_HOST', 'GB_MQ_USER', 'GB_MQ_PASS','GB_MQ_EPG_QUEUE' ,
            'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB', 'POSTGRES_HOST']:
    if not os.environ.get(var):
        eprint(f"Please set ENVIRONMENT veriable {var!r}")
        sys.exit(-1)
    gb_env[var] = os.environ[var]
   
mq_queue = gb_env['GB_MQ_EPG_QUEUE'] 
table_name = mq_queue

table_struct = ( f"create table {table_name} ("+
                "ID              SERIAL PRIMARY KEY," +
                "channel         varchar(127)," +
                "channelSid      int," +
                "programName     varchar(255)," +
                "programStart    real," +
                "programEnd      real" +
                ")" )
    
def db_connection():
    global gb_env, db_conn, db_cur, table_name
    while True: 
        try:
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
    try:
        db_cur.execute(f"select * from {table_name}")
    except :
        lprint()
        eprint(f"Try to create table: {table_struct}")
        db_cur.execute(table_struct)
    eprint(f"Connected to PostgreSQL host {gb_env['POSTGRES_HOST']}, db {gb_env['POSTGRES_DB']}")

def start():
    credentials = pika.PlainCredentials(gb_env['GB_MQ_USER'], gb_env['GB_MQ_PASS'])
    parameters = pika.ConnectionParameters(
            gb_env['GB_MQ_HOST'], 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    '''
    channel.queue_declare(
            queue=mq_queue, 
            passive=False, 
            durable=True,  
            exclusive=False, 
            auto_delete=False)
    '''
    def callback(ch, method, properties, body):
        global db_cur
        try:
            if not db_cur:
                eprint('invalid db cursor')
                return
            rec = json.loads(body.decode())
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
            eprint(f"Try to run {insert}")
            db_cur.execute(insert)
        except :
            lprint()
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
        except :
            lprint()
        time.sleep(15)
