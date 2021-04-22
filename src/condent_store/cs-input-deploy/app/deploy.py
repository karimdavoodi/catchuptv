import json
import yaml
from kubernetes import client, config

import base_yaml

def kube_apply_pod_file(rec):
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    
    pass

def kube_apply_dep_channel(rec):
                 
    pass

def kube_delete(db_path:str, body:str):
        rec = json.loads(body)


def kube_apply(db_path:str, body:str):
    rec = json.loads(body)
    if '/cs/vod' in db_path:
        kube_apply_pod_file(rec)
    if '/cs/channel' in db_path:
        kube_apply_dep_channel(rec)


config.load_incluster_config()
v1 = client.AppsV1Api()
resp = v1.create_namespaced_deployment(body=base_yaml.file_job, namespace="default")
print("Deployment created. status='%s'" % resp.metadata.name)
