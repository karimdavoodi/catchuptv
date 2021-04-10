import redis
import time

r = redis.Redis(host='live-cache', port=6379, password='31233123')

r.set('channel 1:last_seq',209)
r.set('channel 1:seq:209','bbbb',10)
r.set('channel 1:seq:208',102,4)
r.set('channel 1:seq:208',100,4)
r.set('channel 1:seq:208',107,4)
while True:
    print(r.get('channel 1:seq:208'))
    time.sleep(1)
print(r.get('key1'))
