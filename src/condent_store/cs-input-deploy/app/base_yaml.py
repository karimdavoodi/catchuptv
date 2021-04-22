file_job = {
  "apiVersion": "batch/v1",
  "kind": "Job",
  "metadata": {
    "name": "cs-file-to-hls",
  },
  "spec": {
    "template": {
      "spec": {
        "volumes": [
          {
            "name": "hls-out",
            "emptyDir": {
              "medium": "Memory"
            }
          }
        ],
        "containers": [
          {
            "name": "cs-file-to-hls",
            "image": "cs-live-to-hls",
            "volumeMounts": [
              {
                "name": "hls-out",
                "mountPath": "/hls"
              }
            ],
            "env": [
              {
                "name": "CHANNEL_NAME",
                "value": "test channel"
              },
              {
                "name": "CHANNEL_DAILY_START",
                "value": "00:00"
              },
              {
                "name": "CHANNEL_DAILY_STOP",
                "value": "23:59"
              },
              {
                "name": "CHANNEL_URL",
                "value": "https://tv.razavi.ir/hls/rozeh_1.m3u8"
              },
              {
                "name": "CHANNEL_BANDWIDTH",
                "value": "1000000"
              },
              {
                "name": "HLS_VIDEO_CODEC",
                "value": "copy"
              },
              {
                "name": "HLS_VIDEO_SIZE",
                "value": "1280x720"
              },
              {
                "name": "HLS_VIDEO_FPS",
                "value": "25"
              },
              {
                "name": "HLS_AUDIO_CODEC",
                "value": "copy"
              },
              {
                "name": "HLS_AUDIO_BITRATE",
                "value": "128k"
              }
            ]
          }
        ]
      }
    }
  }
}

channel = {

  "apiVersion": "apps/v1",
  "kind": "Deployment",
  "metadata": {
    "name": "cs-live-to-hls-dep",
    "labels": {
      "tire": "channel",
      "topic": "hls"
    }
  },
  "spec": {
    "selector": {
      "matchLabels": {
        "app": "cs-live-to-hls"
      }
    },
    "replicas": 1,
    "template": {
      "metadata": {
        "labels": {
          "app": "cs-live-to-hls",
          "topic": "hls"
        }
      },
      "spec": {
        "volumes": [
          {
            "name": "hls-out",
            "emptyDir": {
              "medium": "Memory"
            }
          }
        ],
        "containers": [
          {
            "name": "cs-live-to-hls",
            "image": "cs-live-to-hls",
            "volumeMounts": [
              {
                "name": "hls-out",
                "mountPath": "/hls"
              }
            ],
            "env": [
              {
                "name": "CHANNEL_NAME",
                "value": "test channel"
              },
              {
                "name": "CHANNEL_DAILY_START",
                "value": "00:00"
              },
              {
                "name": "CHANNEL_DAILY_STOP",
                "value": "23:59"
              },
              {
                "name": "CHANNEL_URL",
                "value": "https://tv.razavi.ir/hls/rozeh_1.m3u8"
              },
              {
                "name": "CHANNEL_BANDWIDTH",
                "value": "1000000"
              },
              {
                "name": "HLS_VIDEO_CODEC",
                "value": "copy"
              },
              {
                "name": "HLS_VIDEO_SIZE",
                "value": "1280x720"
              },
              {
                "name": "HLS_VIDEO_FPS",
                "value": "25"
              },
              {
                "name": "HLS_AUDIO_CODEC",
                "value": "copy"
              },
              {
                "name": "HLS_AUDIO_BITRATE",
                "value": "128k"
              }
            ]
          }
        ],
        "initContainers": [
          {
            "name": "wait-for-mq",
            "image": "busybox:1.28",
            "command": [
              "sh",
              "-c",
              "until nslookup $CS_GB_MQ_SERVICE_HOST; do echo 'Wait for gb-mq'; sleep 3; done"
            ]
          }
        ]
      }
    }
  }
}
