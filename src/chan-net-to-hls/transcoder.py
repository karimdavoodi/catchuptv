#!/usr/bin/python3
from __future__ import print_function
import os
import sys
import time
import pika
import pyinotify
from threading import Thread

gb_env = {}
channel_seg = None


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
        'GB_MQ_SEG_QUEUE']:
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
    hls_attr = "-hls_time 5 -hls_list_size 5 -hls_flags delete_segments "  \
            "-hls_flags second_level_segment_duration+second_level_segment_index " \
            "-strftime 1 -hls_segment_filename \"/hls/%%d_%s_%%t.ts\" " \
            "-f hls /hls/p.m3u8"
    cmd = "ffmpeg -v quiet "
    cmd += f"-i {gb_env['CHANNEL_URL']!r} {smap} {video_attr} {audio_attr} {hls_attr}"
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

def send_seg_to_mq(info, file_path):
    global channel_seg

    with open(file_path, 'rb') as f:
        merg = bytearray(str(info).encode())
        for i in range(255-len(merg)):
            merg.extend(' '.encode('latin-1'))
        merg.extend(f.read())
        eprint(f"Try to send data to MQ by len:{len(merg)}")
        try:
            channel_seg.basic_publish( exchange='', 
                routing_key=gb_env['GB_MQ_SEG_QUEUE'],
                body=merg)
        except Exception as err:
            eprint(str(err))
            eprint("Try to connect MQ again!")
            init_mq()
             
def init_mq():
    global channel_seg
    while True:
        try:
            credentials = pika.PlainCredentials(gb_env['GB_MQ_USER'], gb_env['GB_MQ_PASS'])
            parameters = pika.ConnectionParameters(
                    gb_env['GB_MQ_HOST'], 5672, '/', credentials)
            connection_data = pika.BlockingConnection(parameters)
            channel_seg = connection_data.channel()
            channel_seg.queue_declare(
                    queue=gb_env['GB_MQ_SEG_QUEUE'], 
                    passive=False, 
                    durable=True,  
                    exclusive=False, 
                    auto_delete=False)
            break
        except Exception as err:
            eprint(str(err))
            time.sleep(10)

    eprint('Connect to '+gb_env['GB_MQ_HOST'])

def watch_segments():
    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm)

    def callback(event):
        try:
            seg = event.name.split('_')
            if len(seg)>2:
                seq = int(seg[0])
                start = float(seg[1])
                duration = float(seg[2][:-3]) / 1000000
                info = {
                    'channel': gb_env['CHANNEL_NAME'],
                    'sequence': seq,
                    'start': start,
                    'duration': duration
                    }
                send_seg_to_mq(info, event.pathname)
        except Exception as err:
            eprint(str(err))
    eprint(f"Watch to /hls")
    wm.add_watch('/hls', pyinotify.IN_MOVED_TO, callback)
    notifier.loop()

if __name__ == '__main__':
    init_mq()
    start_ffmpeg_thread()
    watch_segments()
