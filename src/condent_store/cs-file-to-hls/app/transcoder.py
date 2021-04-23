#!/usr/bin/python3
import os
import time
import json
import pyinotify
import subprocess
from threading import Thread

import util
import rabbitmq

job_finish = False
gb_env = util.get_env([
        'CS_GB_MQ_SERVICE_HOST',
        'GB_MQ_USER',
        'GB_MQ_PASS',
        'FILE_IMPORT_DELAY',
        'FILE_NAME',
        'FILE_BANDWIDTH',
        'FILE_URL',
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

def start_ffmpeg_thread():
    codec = gb_env['HLS_VIDEO_CODEC'].lower()
    vtranscode = False if ('copy' == codec or len(codec)<2) else True
    codec = gb_env['HLS_AUDIO_CODEC'].lower()
    atranscode = False if ('copy' == codec or len(codec)<2) else True
    if vtranscode:
        codec = '-vcodec ' + gb_env.get('HLS_VIDEO_CODEC','libx264')
        size = '-s ' + gb_env.get('HLS_VIDEO_SIZE', '1280x720')
        b = float(gb_env.get('FILE_BANDWIDTH', '2'))
        if b < 100: b = int(b * 1000000)
        bitrate = '-b:v ' + str(b)
        frame = '-r ' + gb_env.get('HLS_VIDEO_FPS', '24')
        video_attr = f"{codec} {size} {bitrate} {frame} -g 24"
    else:
        video_attr = "-vcodec copy"
    if atranscode:
        codec = '-acodec ' + gb_env.get('HLS_AUDIO_CODEC', 'aac')
        b = float(gb_env.get('HLS_AUDIO_BITRATE', '128'))
        if b < 1000: b = int(b * 1000)
        bitrate = '-b:a ' + str(b)
        audio_attr = f"{codec} {bitrate}"
    else:
        audio_attr = "-acodec copy"
    smap = '-map v -map a'
    hls_attr = "-hls_time 5 -hls_list_size 5 -hls_flags delete_segments "  \
            "-hls_flags second_level_segment_duration+second_level_segment_index " \
            "-strftime 1 -hls_segment_filename \"/hls/%%d_%s_%%t.ts\" " \
            "-f hls /hls/p.m3u8"
    cmd = "ffmpeg -re "
    cmd += f"-i {gb_env['FILE_URL']!r} {smap} {video_attr} {audio_attr} {hls_attr} "
    util.info(cmd)
    os.system(cmd)
    util.info('Import finished. Exit')
    job_finish = True

def send_seg_to_mq(info, file_path):
    global mq

    util.debug(info)
    with open(file_path, 'rb') as f:
        merg = bytearray(json.dumps(info).encode())
        for i in range(512-len(merg)):
            merg.extend(' '.encode('latin-1'))
        merg.extend(f.read())
        mq.publish(merg)
            
first_seg_time = 0
def watch_segments():
    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm)
    def callback(event):
        global first_seg_time, job_finish
        try:
            seg = event.name.split('_')
            if len(seg)>2:
                seq = int(seg[0])
                start = int(seg[1])
                duration = float(seg[2][:-3]) / 1000000
                if first_seg_time == 0:
                    first_seg_time = start
                info = {
                    "file": gb_env["FILE_NAME"],
                    "bandwidth": gb_env['FILE_BANDWIDTH'],
                    "resolution": gb_env['HLS_VIDEO_SIZE'],
                    "sequence": seq,
                    "start": start - first_seg_time,
                    "duration": duration
                    }
                send_seg_to_mq(info, event.pathname)
        except:
            util.trace()
        return job_finish

    util.eprint(f"Watch to /hls")
    wm.add_watch('/hls', pyinotify.IN_MOVED_TO, callback)
    notifier.loop()

def probe_orignal_resolution(url):

    cmd = ("/usr/bin/ffprobe -probesize 100000000 " + 
        "-select_streams v:0 -show_entries stream=width,height " + 
        "-of csv=s=x:p=0 " + f"{url!r}")
    for _ in range(3):
        out = subprocess.check_output(cmd, shell=True).decode().rstrip()
        if len(out) > 1: break
        util.error("Can't probe {url}")
        time.sleep(10)
    util.info(f"Resolution of {url} is {out}")
    return out

if __name__ == '__main__':

    util.info('Delay before start: ' + gb_env['FILE_IMPORT_DELAY'])
    time.sleep(int(gb_env['FILE_IMPORT_DELAY']))
    
    orig_resolution = probe_orignal_resolution(gb_env['FILE_URL'])
    if orig_resolution == "":
        util.error(f"Can't probe {gb_env['FILE_URL']}")
        exit(0)

    if gb_env['HLS_VIDEO_SIZE'] == 'original':
        gb_env['HLS_VIDEO_SIZE'] = orig_resolution 

    t = Thread(target=start_ffmpeg_thread)
    t.start()

    watch_segments()
    t.join()
