#!/usr/bin/python3
import os
import time
import json
import pyinotify
from threading import Thread

import util
import rabbitmq

gb_env = util.get_env([
        'CS_GB_MQ_SERVICE_HOST',
        'GB_MQ_USER',
        'GB_MQ_PASS',
        'CHANNEL_NAME',
        'CHANNEL_BANDWIDTH',
        'CHANNEL_URL',
        'CHANNEL_LIVE',
        'CHANNEL_DAILY_START',
        'CHANNEL_DAILY_STOP',
        'HLS_VIDEO_CODEC',
        'HLS_VIDEO_SIZE',
        'HLS_VIDEO_FPS',
        'HLS_AUDIO_CODEC',
        'HLS_AUDIO_BITRATE',
        'GB_MQ_SEG_QUEUE'])

mq = rabbitmq.MQ_direct(
        host = gb_env['CS_GB_MQ_SERVICE_HOST'],       
        user = gb_env['GB_MQ_USER'],       
        passwd = gb_env['GB_MQ_PASS'],  
        queue  = gb_env['GB_MQ_SEG_QUEUE'],  
        ttl = 60000
        )

def time_to_stop():
    try:
        stop = time.strptime(gb_env['CHANNEL_DAILY_STOP'], '%H:%M')
        now = time.localtime()
        now_s  = now.tm_hour*3600 + now.tm_min*60 + now.tm_sec
        stop_s  = stop.tm_hour*3600 + stop.tm_min*60 + stop.tm_sec
        diff = stop_s - now_s if now_s < stop_s else 86400 - now_s
        util.eprint(f"Wait {diff} second to stop")
        return diff
    except:
        util.lprint()
    return 86400

def time_to_start():
    try:
        start = time.strptime(gb_env['CHANNEL_DAILY_START'], '%H:%M')
        now = time.localtime()
        now_s  = now.tm_hour*3600 + now.tm_min*60 + now.tm_sec
        start_s  = start.tm_hour*3600 + start.tm_min*60 + start.tm_sec
        diff = 1 if now_s > start_s else start_s - now_s
        util.eprint(f"Wait {diff} second to start")
        return diff
    except:
        util.lprint()
    return 1
   
def make_daemon(func_name, func_args:str = ""):
    if func_args == "":
        t = Thread(target=func_name)
    else:
        t = Thread(target=func_name, args=[func_args])
    t.setDaemon(True)
    t.start()

def sys_run_loop_forever(cmd:str):
    def run_loop(cmd:str):
        while True:
            time.sleep(time_to_start())
            util.eprint("Run:" + cmd)
            os.system(cmd)
    make_daemon(run_loop, func_args=cmd)

def start_ffmpeg_thread():
    codec = gb_env['HLS_VIDEO_CODEC'].lower()
    vtranscode = False if ('copy' == codec or len(codec)<2) else True
    codec = gb_env['HLS_AUDIO_CODEC'].lower()
    atranscode = False if ('copy' == codec or len(codec)<2) else True
    if vtranscode:
        codec = '-vcodec ' + gb_env['HLS_VIDEO_CODEC']
        size = '-s ' + gb_env['HLS_VIDEO_SIZE'] \
                if len(gb_env['HLS_VIDEO_SIZE'])>1 else ''
        bitrate = '-b:v ' + gb_env['CHANNEL_BANDWIDTH'] \
                if len(gb_env['CHANNEL_BANDWIDTH'])>1 else ''
        frame = '-r ' + gb_env['HLS_VIDEO_FPS'] \
                if len(gb_env['HLS_VIDEO_FPS'])>1 else ''
        video_attr = f"{codec} {size} {bitrate} {frame}"
    else:
        video_attr = "-vcodec copy"
    if atranscode:
        codec = '-acodec ' + gb_env['HLS_AUDIO_CODEC']
        bitrate = '-b:a ' + gb_env['HLS_AUDIO_BITRATE'] \
                if len(gb_env['HLS_AUDIO_BITRATE'])>1 else ''
        audio_attr = f"{codec} {bitrate}"
    else:
        audio_attr = "-acodec copy"
    smap = '-map v -map a'
    hls_attr = "-hls_time 5 -hls_list_size 5 -hls_flags delete_segments "  \
            "-hls_flags second_level_segment_duration+second_level_segment_index " \
            "-strftime 1 -hls_segment_filename \"/hls/%%d_%s_%%t.ts\" " \
            "-f hls /hls/p.m3u8"
    is_live = True if gb_env['CHANNEL_LIVE'].lower() == 'true' else False
    cmd = "ffmpeg "
    if not is_live:
        util.eprint('channel is VOD, run in play time(-re)')
        cmd += '-re '
    tm = "-t %d" % time_to_stop()
    cmd += f"-i {gb_env['CHANNEL_URL']!r} {tm} {smap} {video_attr} {audio_attr} {hls_attr}"
    sys_run_loop_forever(cmd)


def send_seg_to_mq(info, file_path):
    global mq

    with open(file_path, 'rb') as f:
        merg = bytearray(json.dumps(info).encode())
        for i in range(512-len(merg)):
            merg.extend(' '.encode('latin-1'))
        merg.extend(f.read())
        mq.publish(merg)
            

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
                    "channel": gb_env["CHANNEL_NAME"],
                    "bandwidth": gb_env['CHANNEL_BANDWIDTH'],
                    "resolution": gb_env['HLS_VIDEO_SIZE'],
                    "sequence": seq,
                    "start": start,
                    "duration": duration
                    }
                send_seg_to_mq(info, event.pathname)
        except:
            util.lprint()
    util.eprint(f"Watch to /hls")
    wm.add_watch('/hls', pyinotify.IN_MOVED_TO, callback)
    notifier.loop()


if __name__ == '__main__':
    start_ffmpeg_thread()
    watch_segments()
