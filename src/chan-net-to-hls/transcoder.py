#!/usr/bin/python3
from __future__ import print_function
import os
import sys
import time
import pika
from threading import Thread

gb_env = {}
channel_info = None
channel_data = None
seg_queue = []


def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, flush=True, **kwargs)

for var in [
        'GB_MQ_HOST', 
        'GB_MQ_USER', 
        'GB_MQ_PASS', 
        'CHANNEL_NAME',
        'CHANNEL_URL',
        'HLS_VIDEO_CODEC',
        'HLS_VIDEO_BITRATE',
        'HLS_VIDEO_SIZE',
        'HLS_VIDEO_FPS',
        'HLS_AUDIO_CODEC',
        'HLS_AUDIO_BITRATE',
        'GB_MQ_SEG_INFO_QUEUE',
        'GB_MQ_SEG_DATA_QUEUE']:
    if not os.environ.get(var):
        eprint(f"Please set ENVIRONMENT veriable {var!r}")
        sys.exit(-1)
    gb_env[var] = os.environ[var]

def start_ffmpeg_thread():
    codec = gb_env['HLS_VIDEO_CODEC'].lower()
    vtranscode = False if ('copy' == codec or len(codec)<2) else True
    codec = gb_env['HLS_AUDIO_CODEC'].lower()
    atranscode = False if ('copy' == codec or len(codec)<2) else True
    if vtranscode:
        codec = '-vcodec ' + gb_env['HLS_VIDEO_CODEC']
        size = '-s ' + gb_env['HLS_VIDEO_SIZE'] if len(gb_env['HLS_VIDEO_SIZE'])>1 else ''
        bitrate = '-b:v ' + gb_env['HLS_VIDEO_BITRATE'] if len(gb_env['HLS_VIDEO_BITRATE'])>1 else ''
        frame = '-r ' + gb_env['HLS_VIDEO_FPS'] if len(gb_env['HLS_VIDEO_FPS'])>1 else ''
        video_attr = f"{codec} {size} {bitrate} {frame}"
    else:
        video_attr = "-vcodec copy"
    if atranscode:
        codec = '-acodec ' + gb_env['HLS_AUDIO_CODEC']
        bitrate = '-b:a ' + gb_env['HLS_AUDIO_BITRATE'] if len(gb_env['HLS_AUDIO_BITRATE'])>1 else ''
        audio_attr = f"{codec} {bitrate}"
    else:
        audio_attr = "-acodec copy"
    smap = '-map v -map a'
    hls_attr = "-hls_time 5 -hls_list_size 5 -hls_flags delete_segments"
    output = "-f hls /hls/p.m3u8"
    cmd = f"ffmpeg -i {gb_env['CHANNEL_URL']!r} {smap} {video_attr} {audio_attr} {hls_attr} {output}"
    sys_run_loop_forever(cmd)

def make_daemon(func_name, func_args:str = ""):
    if func_args == "":
        t = Thread(target=func_name)
    else:
        t = Thread(target=func_name, args=[func_args])
    t.setDaemon(True)
    t.start()

def sys_run_loop_forever(cmd:str):

    def run_loop(cmd:str):
        eprint(f"Run:" + cmd)
        while True:
            time.sleep(1)
            os.system(cmd)
            eprint("Re Exceute :"+cmd)
    make_daemon(run_loop, func_args=cmd)

def send_seg_data_to_mq(info, file_path):
    with open(file_path, 'rb') as f:
        merg = bytearray()
        merg.append(str(info).encode())
        for i in range(255-len(merg)):
            merg.append(' '.encode())
        merg.append(f.read())
        eprint(f"Try to send data to MQ by len:{len(info)}")
        channel_data.basic_publish( exchange='', 
                routing_key=gb_env['GB_MQ_SEG_DATA_QUEUE'],
                body=merg)

def send_seg_info_to_mq(info):
    eprint(f"Try to send info to MQ:{str(info)}")
    channel_data.basic_publish( exchange='', 
            routing_key=gb_env['GB_MQ_SEG_DATA_QUEUE'],
            body=str(info))

def parse_playlist():
    dur = ""
    with open('/hls/p.m3u8','rt') as f:
        for l in f:
            if '#EXTINF' in l:
                seg_dur = float(l.split(':')[1].split(',')[0])
            elif '.ts' in l:
                name = l.rstrip()
                if name in seg_queue: continue
                seg_queue.append(name)
                if len(seg_queue) > 100: seg_queue.pop(0)
                seg_start = float(name.split('.ts')[0])
                info = {
                    'channel': gb_env['CHANNEL_NAME'],
                    'start': seg_start,
                    'duration': seg_dur
                    }
                send_seg_info_to_mq(info)
                send_seg_data_to_mq(info, name)


def push_to_mq():
    last_time = 0
    while True:
        time.sleep(5)
        try:
            if os.path.exists('/hls/p.m3u8'):
                p_time = os.stat('/hls/p.m3u8').st_mtime
                if p_time != last_time:
                    parse_playlist()
                last_time = p_time
            else:
                eprint("Not found play list!")
        except Exception as err:
            eprint(str(err))
             
def init_mq():
    
    credentials = pika.PlainCredentials(gb_env['GB_MQ_USER'], gb_env['GB_MQ_PASS'])
    parameters = pika.ConnectionParameters(
            gb_env['GB_MQ_HOST'], 5672, '/', credentials)
    connection_info = pika.BlockingConnection(parameters)
    channel_info = connection_info.channel()
    channel_info.queue_declare(
            queue=gb_env['GB_MQ_SEG_INFO_QUEUE'], 
            passive=False, 
            durable=True,  
            exclusive=False, 
            auto_delete=False)
    connection_data = pika.BlockingConnection(parameters)
    channel_data = connection_data.channel()
    channel_data.queue_declare(
            queue=gb_env['GB_MQ_SEG_DATA_QUEUE'], 
            passive=False, 
            durable=True,  
            exclusive=False, 
            auto_delete=False)
    eprint('Init MQ')

if __name__ == '__main__':
    init_mq()
    start_ffmpeg_thread()
    push_to_mq()
