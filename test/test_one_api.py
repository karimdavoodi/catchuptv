import requests
import json
import time
import shutil
import os
import random
import subprocess
sample_movie = {
        'name': 'test1',
        'sourceUrl': 'https://tv.razavi.ir/hls/rozeh_1.m3u8',
        'icon': 'in db',
        'date': 2020,
        'language': 'en',
        'country': 'tr',
        'bitrates': [
            {
                'bandwidth': 2000000,
                'resolution': 'original'
            },{
                'bandwidth': 1000000,
                'resolution': '720x480'
            }],
        'title':[
            {
                'language': 'en',
                'text': 'the new channel'
            }],
        'description':[
            { 
                'language': 'en',
                'text': 'the new channel description'
            }],
        'category':[ 'id' ],
        'keyword':[ 'key1', 'key2' ],
        'rateIMDb': 7.1,
        'rateAge': 13,
        'rateStar': 3.5,
  	'episodeNumber': 0,
  	'thumbnailPiont': 200,
  	'subtitle':[
	    {
                'language': 'en',
                'url': 'http://...'
	    }
	]	
	
}
sample_channel = {
        'name': 'test1',
        'sourceUrl': 'https://tv.razavi.ir/hls/rozeh_1.m3u8',
        'epgUrl': 'https://tv.razavi.ir/hls/rozeh_1.m3u8',
        'dailyStart': '00:00',
        'dailyStop': '23:59',
        'icon': 'in db',
        'language': 'en',
        'country': 'tr',
        'bitrates': [
            {
                'bandwidth': 2000000,
                'resolution': 'original'
            },{
                'bandwidth': 1000000,
                'resolution': '720x480'
            }],
        'title':[
            {
                'language': 'en',
                'text': 'the new channel'
            }],
        'description':[
            { 
                'language': 'en',
                'text': 'the new channel description'
            }],
        'category':[ 'id' ],
        'keyword':[ 'key1', 'key2' ],
        'rateAge': 13,
        'rateStar': 3.5
}
cmd = 'minikube service -n kong kong-proxy --url'          
base_url = subprocess.run(cmd.split(), 
        stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')[0].rstrip()
base_url += '/v1/cs/info/manage'

def add_channel():
    chan = sample_channel
    chan['name'] = 'channel ' + str(random.randint(1,1000000)) 
    ret = requests.put( base_url + '/cs')
    ret = requests.put( base_url + '/cs/channel')
    ret = requests.post( base_url + '/cs/channel', json = chan)

def add_movie():
    chan = sample_movie
    chan['name'] = 'channel ' + str(random.randint(1,1000000)) 
    ret = requests.put( base_url + '/cs')
    ret = requests.put( base_url + '/cs/vod')
    ret = requests.post( base_url + '/cs/vod', json = chan)

