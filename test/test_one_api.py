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
    ret = requests.put( base_url + '/cs/channel')
    ret = requests.post( base_url + '/cs/channel', json = chan)

def add_movie():
    chan = base_yaml.sample_movie
    chan['name'] = 'channel ' + str(random.randint(1,1000000)) 
    ret = requests.put( base_url + '/cs')
    ret = requests.put( base_url + '/cs/vod')
    ret = requests.post( base_url + '/cs/vod', json = chan)

