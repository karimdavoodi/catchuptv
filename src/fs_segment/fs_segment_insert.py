#!/usr/bin/gb_env python
import os
import sys
import pika
import json
import time
import psycopg2

channels_content_root = '/data/'
gb_env = {}

for var in ['MQ_HOST', 'MQ_QUEUE', 'MQ_USER', 'MQ_PASS']:
    if not os.environ.get(var):
        print(f"Please set ENVIRONMENT veriable {var!r}")
        sys.exit(-1)
    gb_env[var] = os.environ[var]
    


def start():
    credentials = pika.PlainCredentials(gb_env['MQ_USER'], gb_env['MQ_PASS'])
    parameters = pika.ConnectionParameters(
            gb_env['MQ_HOST'], 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue=gb_env['MQ_QUEUE'], durable=True)

    def callback(ch, method, properties, body):
        try:
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

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=gb_env['MQ_QUEUE'], on_message_callback=callback)
    channel.start_consuming()

if __name__ == '__main__':
    while True:
        try:
            print("Start insert process")
            start()
        except Exception as err:
            print('Error(2):', str(err))
        time.sleep(15)
