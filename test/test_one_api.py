import requests
import json
import time
import shutil
import os
import random
import subprocess

import base_yaml

cmd = 'minikube service -n kong kong-proxy --url'          
base_url = subprocess.run(cmd.split(), 
        stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')[0].rstrip()
base_url += '/v1/cs/info/manage'

def add_channel():
    chan = base_yaml.sample_channel
    chan['name'] = 'channel ' + str(random.randint(1,1000000)) 
    ret = requests.put( base_url + '/cs')
    print(ret.text)
    ret = requests.put( base_url + '/cs/channel')
    print(ret.text)
    ret = requests.post( base_url + '/cs/channel', json = chan)
    print(ret.text)

def add_movie():
    chan = base_yaml.sample_movie
    chan['name'] = 'file ' + str(random.randint(1,1000000)) 
    chan['sourceUrl'] = 'http://192.168.1.30/1.mp4'
    ret = requests.put( base_url + '/cs')
    print(ret.text)
    ret = requests.put( base_url + '/cs/vod')
    print(ret.text)
    ret = requests.post( base_url + '/cs/vod', json = chan)
    print(ret.text)

#add_channel()
add_movie()

