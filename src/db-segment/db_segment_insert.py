#!/usr/bin/gb_env python
from __future__ import print_function
import os
import sys
import pika
import json
import time
import psycopg2

DB_HOST="localhost"
DB_DATABASE="epg"
DB_USER="postgres"
DB_PASS="31233123"
    
gb_env = {}
db_conn = None
db_cur = None

def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)
        
for var in ['GB_MQ_HOST', 'GB_MQ_SEG_INFO_QUEUE', 'GB_MQ_USER', 'GB_MQ_PASS']:
    if not os.environ.get(var):
        eprint(f"Please set ENVIRONMENT veriable {var!r}")
        sys.exit(-1)
    gb_env[var] = os.environ[var]
    

# Connect to PostgreSQL
def db_connection():
    global gb_env, db_conn, db_cur
    
    db_conn = psycopg2.connect(
            host = DB_HOST,
            database = DB_DATABASE,
            user = DB_USER,
            password = DB_PASS)
    db_cur = db_conn.cursor()
    eprint('Connected to PostgreSQL')

def start():
    credentials = pika.PlainCredentials(gb_env['GB_MQ_USER'], gb_env['GB_MQ_PASS'])
    parameters = pika.ConnectionParameters(
            gb_env['GB_MQ_HOST'], 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue=gb_env['GB_MQ_SEG_INFO_QUEUE'], durable=True)
    '''
    channel.exchange_declare(exchange= gb_env['GB_MQ_EXCHANGE'], exchange_type='fanout')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=gb_env['GB_MQ_EXCHANGE'], queue=queue_name)
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
                    "INSERT INTO EPG " + 
                    "(channel, channelSid, programName, programStart, programEnd)" +  
                    "VALUES "+
                    f"({channel!r},{channelSid},{programName!r},{programStart},{programEnd}"
                    )
            db_cur.execute(insert)
            eprint(f"{insert}")
        except Exception as err:
            eprint(f"Error(1): ", str(err))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=gb_env['GB_MQ_SEG_INFO_QUEUE'], on_message_callback=callback)
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
