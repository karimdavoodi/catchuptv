from pprint import pprint
from kubernetes import client, config
'''
config.load_kube_config()

v1=client.CoreV1Api()
print("Listing pods with their IPs:")
ret = v1.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
'''

def add_channel_hls(channel):
    config.load_kube_config()
    with client.ApiClient(config) as api_client:
      api_instance = client.ExtensionsV1beta1Api(api_client)
      body = client.ExtensionsV1beta1Deployment()
      namespace = 'default'

      try:
          api_response = api_instance.create_namespaced_deployment(
                namespace, body)
          pprint(api_response)
      except client.rest.ApiException as e:
          print("Exception : %s\n" % e)

def add_channel_epg():         
    pass                       
def apply_deployment():        
    pass                       
def delete_deployment():       
    pass                       
channel = {
        'CHANNEL_NAME': "test channel",
        'CHANNEL_URL': "https'://tv.razavi.ir/hls/rozeh_1.m3u8",
        'HLS_VIDEO_CODEC': "copy",
        'HLS_VIDEO_BITRATE': "2000k",
        'HLS_VIDEO_SIZE': "1280x720",
        'HLS_VIDEO_FPS': "25",
        'HLS_AUDIO_CODEC': "copy",
        'HLS_AUDIO_BITRATE': "128k",
        }
add_channel_hls(channel)
