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

for var in ['GB_MQ_HOST', 'GB_MQ_EPG_QUEUE', 'GB_MQ_USER', 'GB_MQ_PASS', 
            'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB', 'POSTGRES_HOST']:
    if not os.environ.get(var):
        eprint(f"Please set ENVIRONMENT veriable {var!r}")
        sys.exit(-1)
    gb_env[var] = os.environ[var]

# Connect to PostgreSQL
def db_connection():
    global gb_env, db_conn, db_cur
    
    db_conn = psycopg2.connect(
            host = gb_env['POSTGRES_HOST'],
            database = gb_env['POSTGRES_DB'],
            user = gb_env['POSTGRES_USER'],
            password = gb_env['POSTGRES_PASSWORD'])
    db_cur = db_conn.cursor()
    eprint(f"Connected to PostgreSQL host {gb_env['POSTGRES_HOST']}, db {gb_env['POSTGRES_DB']}")

def write_mq(_queue):
    credentials = pika.PlainCredentials(gb_env['GB_MQ_USER'], gb_env['GB_MQ_PASS'])
    parameters = pika.ConnectionParameters(
            gb_env['GB_MQ_HOST'], 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue=_queue, durable=True)
    message = ' '.join(sys.argv[1:]) or "Hello World!"
    while True:
        time.sleep(3)
        channel.basic_publish( exchange='', routing_key=_queue, body=message)
        eprint(" [x] Sent %r" % message)
    connection.close()



def read_mq(_queue):
    credentials = pika.PlainCredentials(gb_env['GB_MQ_USER'], gb_env['GB_MQ_PASS'])
    parameters = pika.ConnectionParameters(
            gb_env['GB_MQ_HOST'], 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue=_queue, durable=True)

    def callback(ch, method, properties, body):
        global db_cur
        try:
            rec = body.decode()
            eprint(rec)
        except Exception as err:
            eprint(f"Error(1): ", str(err))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    eprint(f"Wait for MQ on host {gb_env['GB_MQ_HOST']}, queue {_queue}")
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=_queue, on_message_callback=callback)
    channel.start_consuming()

if __name__ == '__main__':
    queue = sys.argv[1]
    eprint("Start insert process")
    #db_connection()
    read_mq(queue)
