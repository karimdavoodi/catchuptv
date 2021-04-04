#!/usr/bin/gb_env python
import os
import sys
import pika
import json
import time
import psycopg2

gb_env = {}
db_conn = None
db_cur = None

for var in ['MQ_HOST', 'MQ_QUEUE', 'MQ_USER', 'MQ_PASS',
        'DB_HOST', 'DB_DATABASE', 'DB_USER', 'DB_PASS']:
    if not os.environ.get(var):
        print(f"Please set ENVIRONMENT veriable {var!r}")
        sys.exit(-1)
    gb_env[var] = os.environ[var]
    

# Connect to PostgreSQL
def db_connection():
    global gb_env, db_conn, db_cur
    
    db_conn = psycopg2.connect(
        host = gb_env['DB_HOST'],
        database = gb_env['DB_DATABASE'],
        user = gb_env['DB_USER'],
        password = gb_env['DB_PASS'])
    db_cur = db_conn.cursor()
    print('Connected to PostgreSQL')

def start():
    credentials = pika.PlainCredentials(gb_env['MQ_USER'], gb_env['MQ_PASS'])
    parameters = pika.ConnectionParameters(
            gb_env['MQ_HOST'], 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue=gb_env['MQ_QUEUE'], durable=True)

    def callback(ch, method, properties, body):
        global db_cur
        try:
            if not db_cur:
                print('invalid db cursor')
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
            print(f"{insert}")
        except Exception as err:
            print(f"Error(1): ", str(err))
        ch.basic_ack(delivery_tag=method.delivery_tag)


    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=gb_env['MQ_QUEUE'], on_message_callback=callback)
    channel.start_consuming()


if __name__ == '__main__':
    while True:
        try:
            print("Start insert process")
            db_connection()
            start()
        except Exception as err:
            print('Error(2):', str(err))
        time.sleep(15)
