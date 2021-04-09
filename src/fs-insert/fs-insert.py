#!/usr/bin/python3
from __future__ import print_function
import os
import sys
import pika
import json
import time

channels_content_root = '/data/'
gb_env = {}

def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, flush=True, **kwargs)

for var in ['GB_MQ_HOST', 'GB_MQ_USER', 'GB_MQ_PASS','GB_MQ_SEQ_QUEUE', 
            'MQ_CACHE_HOST', 'MQ_CACHE_QUEUE', 'MQ_CACHE_USER', 'MQ_CACHE_PASS']:
    if not os.environ.get(var):
        print(f"Please set ENVIRONMENT veriable {var!r}")
        sys.exit(-1)
    gb_env[var] = os.environ[var]
    

def start():
    # INIT SRC
    credentials = pika.PlainCredentials(gb_env['GB_MQ_USER'], gb_env['GB_MQ_PASS'])
    parameters = pika.ConnectionParameters(gb_env['GB_MQ_HOST'], 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    src_channel = connection.channel()
    src_channel.queue_declare(
            queue=gb_env['GB_MQ_SEG_QUEUE'], 
            passive=False, 
            durable=True,  
            exclusive=False, 
            auto_delete=False)
    # INIT DEST
    _credentials = pika.PlainCredentials(gb_env['MQ_CACHE_USER'], gb_env['MQ_CACHE_PASS'])
    _parameters = pika.ConnectionParameters(gb_env['MQ_CACHE_HOST'], 5672, '/', _credentials)
    _connection = pika.BlockingConnection(parameters)
    dst_channel = _connection.channel()
    dst_channel.queue_declare(
            queue=gb_env['MQ_CACHE_QUEUE'], 
            passive=False, 
            durable=True,  
            exclusive=False, 
            auto_delete=False)

    def callback(ch, method, properties, body):
        try:
            try:
                dst_channel.basic_publish( exchange='', 
                    routing_key=gb_env['MQ_CACHE_QUEUE'],
                    body=body)
            except Exception as err:
                eprint(str(err))
            metadata = json.loads(body[:255].decode())
            start_time = metadata.get('start_time')
            channel_name = metadata.get('channel_name')
            if not start_time or not channel_name:
                print('Invalid medtadata')
                return
            tm = time.localtime(int(start_time))
            seg_path = f"{channel_name}/{tm.tm_year}/{tm.tm_mon}/{tm.tm_mday}/{tm.tm_hour}"
            file_path = f"/{channels_content_root}/{seg_path}/{start_time}.ts"
            with open(file_path, 'wb') as f:
                f.write(body[255:])
                print(f"Write on {file_path}")
        except Exception as err:
            print(f"Error(1): ", str(err))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    src_channel.basic_qos(prefetch_count=1)
    src_channel.basic_consume(queue=gb_env['GB_MQ_SEG_QUEUE'], on_message_callback=callback)
    src_channel.start_consuming()

if __name__ == '__main__':
    while True:
        try:
            print("Start insert process")
            start()
        except Exception as err:
            print('Error(2):', str(err))
        time.sleep(15)
