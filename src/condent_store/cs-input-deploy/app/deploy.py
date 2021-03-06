import json
import string
import random
import sys, os, time
from kubernetes import client, config

import util
import base_yaml

config.load_incluster_config()
job_api = client.BatchV1Api()
dep_api = client.AppsV1Api()


def kube_delete(db_path:str, body:str):
    rec = json.loads(body)
    '''
    if '/cs/vod' in db_path:
        kube_create_file_job(rec)
    if '/cs/live' in db_path:
        kube_create_live_dep(rec)
    '''
     
def kube_create(db_path:str, body:str):
    try:
        try:
            rec = json.loads(body)
        except:
            util.trace()
            util.error(f'Invalid json: {body}')
            return False

        util.info(f"Try to deploy for {rec['name']}")
        if rec.get('sourceUrl','') == '':
            util.error('Empty sourceUrl for live ' + rec['name'])
            return False
        if not kube_test_credentials():
           util.error("Can't connnet to kubernetes!")
           return False

        add_xmltv = False
        bandwidth_list = []
        for bitrate in rec['bitrates']:
            util.info(f"Try to deploy for {rec['name']} bitrate {bitrate['bandwidth']}")
            if bitrate['bandwidth'] in bandwidth_list:
                util.error('Duplicate bandwidth in live ' + rec['name'])
                continue
            bandwidth_list.append(bitrate['bandwidth'])

            if 'cs/live' in db_path:
                live = config_live_dep(rec, base_yaml.live_dep.copy(), bitrate)
                dep_api.create_namespaced_deployment(body = live, namespace = "default")
                util.info("Created Channel Dep: " + live['metadata']['name'])
                if rec.get('epgUrl','') != '' and not add_xmltv:
                    add_xmltv = True
                    xmltv = config_xmltv_dep(rec, base_yaml.xmltv_dep.copy())
                    dep_api.create_namespaced_deployment(body = xmltv, namespace = "default")
                    util.info("Created XMLTV Dep: " + xmltv['metadata']['name'])

            elif 'cs/vod' in db_path:
                job = config_file_job(rec, base_yaml.file_job.copy(), bitrate)
                job_api.create_namespaced_job(body = job, namespace = "default")
                util.info("Created File Job: " + job['metadata']['name'])
                for subtitle in rec.get('subtitle',[]):
                    if subtitle.get('url','') != '':
                        sub = config_subtitle_job(rec, base_yaml.subtitle_job.copy(), subtitle)
                        job_api.create_namespaced_job(body = sub, namespace = "default")
                        util.info("Created Subtitle Job: " + sub['metadata']['name'])
    except:
        util.trace()
        return False
    return True


def config_file_job(rec, template, bitrate):
    file = template
    safe_name = util.uniq_name(rec['name'], '-', False)
    file['metadata']['name'] = f"cs-filetohls-{safe_name}-{bitrate['bandwidth']}" 
    transcode = base_yaml.transcode_profiles.get(bitrate.get('resolution','original'),
            base_yaml.transcode_profiles_def)
    file["spec"]["template"]["spec"]["containers"][0]["env"] = [
          { "name": "FILE_IMPORT_DELAY",
            "value": rec.get("import_delay", "0")
          },
          { "name": "FILE_NAME",
            "value": rec["name"]
          },
          { "name": "FILE_URL",
            "value": rec.get("sourceUrl", "")
          },
          { "name": "FILE_BANDWIDTH",
            "value": str(bitrate["bandwidth"])
          },
          { "name": "HLS_VIDEO_CODEC",
            "value": transcode["HLS_VIDEO_CODEC"]
          },
          { "name": "HLS_VIDEO_SIZE",
            "value": transcode["HLS_VIDEO_SIZE"]
          },
          { "name": "HLS_VIDEO_FPS",
            "value": transcode["HLS_VIDEO_FPS"]
          },
          { "name": "HLS_AUDIO_CODEC",
            "value": transcode["HLS_AUDIO_CODEC"]
          },
          { "name": "HLS_AUDIO_BITRATE",
            "value": transcode["HLS_AUDIO_BITRATE"]
          }
        ]
    util.debug(file)
    return file

def config_xmltv_dep(rec, template):
    epg =  template
    safe_name = util.uniq_name(rec['name'], '-', False)
    epg['metadata']['name'] = f"cs-importepg-{safe_name}" 
    epg["spec"]["template"]["spec"]["containers"][0]["env"] = [
          { "name": "CHANNEL_NAME",
            "value": rec["name"]
          },
          { "name": "XMLTV_URL",
            "value": rec.get('epgUrl', '')
          }
        ]
    util.debug(epg)
    return epg

def config_subtitle_job(rec, template, subtitle):
    sub = template
    safe_name = util.uniq_name(rec['name'], '-', False)
    rand_name = util.uniq_name('', '-', False)
    sub['metadata']['name'] = f"cs-importsub-{safe_name}-{rand_name}" 
    sub["spec"]["template"]["spec"]["containers"][0]["env"] = [
          { "name": "FILE_NAME",
            "value": rec["name"]
          },
          { "name": "SUBTITLE_URL",
            "value": subtitle.get('url', '')
          },
          { "name": "SUBTITLE_LANGUAGE",
            "value": subtitle.get('language','')
          }
        ]
    util.debug(sub)
    return sub

def config_live_dep(rec, template, bitrate):
    live = template
    safe_name = util.uniq_name(rec['name'], '-', False)
    live['metadata']['name'] = f"cs-livetohls-{safe_name}-{bitrate['bandwidth']}" 
    transcode = base_yaml.transcode_profiles.get(bitrate.get('resolution','original'),
            base_yaml.transcode_profiles_def)
    live["spec"]["template"]["spec"]["containers"][0]["env"] = [
          { "name": "CHANNEL_NAME",
            "value": rec["name"]
          },
          { "name": "CHANNEL_DAILY_START",
            "value": rec.get("dailyStart", "00:00")
          },
          { "name": "CHANNEL_DAILY_STOP",
            "value": rec.get("dailyStop", "23:59")
          },
          { "name": "CHANNEL_URL",
            "value": rec.get("sourceUrl", "")
          },
          { "name": "CHANNEL_BANDWIDTH",
            "value": str(bitrate["bandwidth"])
          },
          { "name": "HLS_VIDEO_CODEC",
            "value": transcode["HLS_VIDEO_CODEC"]
          },
          { "name": "HLS_VIDEO_SIZE",
            "value": transcode["HLS_VIDEO_SIZE"]
          },
          { "name": "HLS_VIDEO_FPS",
            "value": transcode["HLS_VIDEO_FPS"]
          },
          { "name": "HLS_AUDIO_CODEC",
            "value": transcode["HLS_AUDIO_CODEC"]
          },
          { "name": "HLS_AUDIO_BITRATE",
            "value": transcode["HLS_AUDIO_BITRATE"]
          }
        ]
    util.debug(live)
    return live


def kube_delete_empty_pods(namespace='default', phase='Succeeded'):
    api_pods = client.CoreV1Api()
    
    pods = api_pods.list_namespaced_pod(namespace,
                include_uninitialized=False,
                pretty=True,
                timeout_seconds=60)

    for pod in pods.items:
        util.info(pod)
        podname = pod.metadata.name
        if pod.status.phase == phase:
            api_response = api_pods.delete_namespaced_pod(podname, namespace)
            util.info("Pod: {} deleted!".format(podname))
            util.debug(api_response)
        else:
            util.info("Pod: {} still not done... Phase: {}".format(
                    podname, pod.status.phase))

def kube_cleanup_finished_jobs(namespace='default', state='Finished'):
    jobs = job_api.list_namespaced_job(namespace,
            include_uninitialized=False,
            pretty=True,
            timeout_seconds=60)
    
    for job in jobs.items:
        util.info(job)
        jobname = job.metadata.name
        jobstatus = job.status.conditions
        if job.status.succeeded == 1:
            util.info("Cleaning up Job: {}. Finished at: {}".format(
                jobname, job.status.completion_time))
            api_response = job_api.delete_namespaced_job(jobname, namespace)
            util.debug(api_response)
        else:
            if jobstatus is None and job.status.active == 1:
                jobstatus = 'active'
            util.info(f"Job: {jobname} not cleaned up. Current status: {jobstatus}")
    
def kube_test_credentials():
    try: 
        api_response = job_api.get_api_resources()
        return True
    except:
        util.trace()
    return False

if __name__ == "__main__" :
    rec = json.dumps(base_yaml.sample_live)
    kube_create('/cs/live', rec)

    rec = json.dumps(base_yaml.sample_movie)
    kube_create('/cs/vod', rec)
