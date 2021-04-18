import pika
import time

import util

class MQ_direct:
    channel = None
    connection = None
    host = ''
    port = 5672
    queue = ''
    vhost = '/'
    user = ''
    passwd = ''
    ttl = 0

    def __init__(self, host, user, passwd, queue, ttl, port = 5672, vhost = '/'):
        self.host = host
        self.port = port 
        self.user = user
        self.passwd =  passwd
        self.vhost = vhost 
        self.queue = queue
        self.ttl = ttl
        self.connect_inifloop()
    
    def connect(self):
        try:
            credentials = pika.PlainCredentials(self.user, self.passwd)
            parameters = pika.ConnectionParameters(self.host, self.port, 
                                    self.vhost, credentials)
            self.connection= pika.BlockingConnection(parameters)
            self.channel= self.connection.channel()
            if self.ttl != 0 :
                args = {'x-message-ttl' : 60000}
            else:
                args = {}
            self.channel.queue_declare(
                    queue = self.queue, 
                    passive = False, 
                    durable = True,  
                    exclusive = False, 
                    auto_delete = False,
                    arguments = args
                    )
            util.eprint(f'Connect to MQ {self.host} to Queue {self.queue}')
            return True
        except:
            util.lprint()
            return False

    def connect_inifloop(self):
        while True:
            if self.connect():
                break
            time.sleep(5)
            util.eprint('Try to Connect to MQ on ' + self.host )
        
    def publish(self, msg):
        try:
            if not self.channel or self.channel.is_closed:
                self.connect_inifloop()

            util.eprint(f"Try to send data to MQ by len:{len(msg)}")
            self.channel.basic_publish(exchange = '', routing_key= self.queue, body = msg)
        except:
            util.lprint()

    def consume(self, callback):
        try:
            if not self.channel or self.channel.is_closed:
                self.connect_inifloop()
                 
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(queue=self.queue, on_message_callback=callback)
            util.eprint(f"Wait on Queue {self.queue} to consume")
            self.channel.start_consuming()
        except:
            util.lprint()
