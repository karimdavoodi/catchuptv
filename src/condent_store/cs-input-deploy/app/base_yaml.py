file_job = {
  "apiVersion": "batch/v1",
  "kind": "Job",
  "metadata": {
    "name": "cs-file-to-hls-job",
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
        "restartPolicy": "Never",
        "containers": [
          {
            "name": "cs-file-to-hls",
            "image": "cs-file-to-hls",
            "imagePullPolicy": "Never",
            "volumeMounts": [
              {
                "name": "hls-out",
                "mountPath": "/hls"
              }
            ],
            "envFrom":[
                {
                "configMapRef":{
                    "name": "cs-gb-mq-config"
                    }
                }
                ],
            "env": [
              { "name": "FILE_NAME", "value": "testfile" },
              { "name": "FILE_URL", "value": "http" },
              { "name": "FILE_BANDWIDTH", "value": "1000000" },
              { "name": "HLS_VIDEO_CODEC", "value": "copy" },
              { "name": "HLS_VIDEO_SIZE", "value": "1280x720" },
              { "name": "HLS_VIDEO_FPS", "value": "25" },
              { "name": "HLS_AUDIO_CODEC", "value": "copy" },
              { "name": "HLS_AUDIO_BITRATE", "value": "128k" }
            ]
          }
        ]
      }
    }
  }
}

subtitle_job = {
  "apiVersion": "batch/v1",
  "kind": "Job",
  "metadata": {
    "name": "cs-subtitle-import-job",
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
        "restartPolicy": "Never",
        "containers": [
          {
            "name": "cs-subtitle-import",
            "image": "cs-subtitle-import",
            "imagePullPolicy": "Never",
            "envFrom":[
                {
                "configMapRef":{
                    "name": "cs-gb-mq-config"
                    }
                }
                ],
            "env": [
              { "name": "FILE_NAME", "value": "testfile" },
              { "name": "SUBTITLE_LANGUAGE", "value": "" },
              { "name": "SUBTITLE_URL", "value": "" }
            ]
          }
        ]
      }
    }
  }
}
channel_dep = {
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
            "imagePullPolicy": "Never",
            "volumeMounts": [
              {
                "name": "hls-out",
                "mountPath": "/hls"
              }
            ],
            "envFrom":[
                {
                "configMapRef":{
                    "name": "cs-gb-mq-config"
                    }
                }
                ],
            "env": [
              { "name": "CHANNEL_NAME", "value": "test channel" },
              { "name": "CHANNEL_DAILY_START", "value": "00:00" },
              { "name": "CHANNEL_DAILY_STOP", "value": "23:59" },
              { "name": "CHANNEL_URL", "value": "http" },
              { "name": "CHANNEL_BANDWIDTH", "value": "1000000" },
              { "name": "HLS_VIDEO_CODEC", "value": "copy" },
              { "name": "HLS_VIDEO_SIZE", "value": "1280x720" },
              { "name": "HLS_VIDEO_FPS", "value": "25" },
              { "name": "HLS_AUDIO_CODEC", "value": "copy" },
              { "name": "HLS_AUDIO_BITRATE", "value": "128k" }
            ]
          }
        ]
      }
    }
  }
}
xmltv_dep = {
  "apiVersion": "apps/v1",
  "kind": "Deployment",
  "metadata": {
    "name": "cs-xmltv-import-dep",
    "labels": {
      "tire": "channel",
      "topic": "hls"
    }
  },
  "spec": {
    "selector": {
      "matchLabels": {
        "app": "cs-xmltv-import"
      }
    },
    "replicas": 1,
    "template": {
      "metadata": {
        "labels": {
          "app": "cs-xmltv-import",
          "topic": "hls"
        }
      },
      "spec": {
        "containers": [
          {
            "name": "cs-xmltv-import",
            "image": "cs-xmltv-import",
            "imagePullPolicy": "Never",
            "envFrom":[
                {
                "configMapRef":{
                    "name": "cs-gb-mq-config"
                    }
                }
                ],
            "env": [
              { "name": "CHANNEL_NAME", "value": "test channel" },
              { "name": "XMLTV_URL", "value": "" }
            ]
          }
        ]
      }
    }
  }
}
########   SAMPLE ###########################
sample_movie = {
        "import_delay": "1",
        "name": "test1",
        "sourceUrl": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
        "icon": "in db",
        "date": 2020,
        "resolution": "HD",
        "language": "en",
        "country": "tr",
  	"thumbnailPiont": 200,
        "movieType":[ "id" ],
        "movieGenres":[ "id" ],
        "rateIMDb": 7.1,
        "rateAge": 13,
        "rateStar": 3.5,
        "bitrates": [
            {
                "bandwidth": 2,
                "resolution": "original"
            },{
                "bandwidth": 1,
                "resolution": "720x480"
            }],
        "title":[
            {
                "language": "en",
                "text": "the new channel"
            }],
        "description":[
            { 
                "language": "en",
                "text": "the new channel description"
            }],
        "tvShow":{
  	    "seasonNumber": 0,
  	    "episodeNumber": 0,
            "episodeTitle": [{"language": "en", "text":""}],
            "episodeDescription": [{"language": "en", "text":""}]
            },
        "cast":{
            "director": [""],
            "writer": [""],
            "artist": [""]
            },
  	"subtitle":[
	    {
                "language": "en",
                "url": "http://..."
	    }
	]	
}
sample_channel = {
        "name": "test1",
        "sourceUrl": "https://tv.razavi.ir/hls/rozeh_1.m3u8",
        "epgUrl": "https://tv.razavi.ir/hls/rozeh_1.m3u8",
        "dailyStart": "00:00",
        "dailyStop": "23:59",
        "icon": "in db",
        "resolution": "HD",
        "language": "en",
        "country": "tr",
        "channelType":[ "id" ],
        "keyword":[ "key1", "key2" ],
        "rateAge": 13,
        "rateStar": 3.5,
        "bitrates": [
            {
                "bandwidth": 3,
                "resolution": "original"
            },{
                "bandwidth": 2,
                "resolution": "SD"
            }],
        "title":[
            {
                "language": "en",
                "text": "the new channel"
            }],
        "description":[
            { 
                "language": "en",
                "text": "the new channel description"
            }]
}
"""
DB collections:
    channel
    vod
    movie_type
    movie_genres
    movie_cast
    channel_type

"""
transcode_profiles_def = {
            "HLS_VIDEO_SIZE": "original",
            "HLS_VIDEO_FPS": "24",
            "HLS_VIDEO_CODEC": "copy",
            "HLS_AUDIO_CODEC": "copy",
            "HLS_AUDIO_BITRATE": "128"
            }
transcode_profiles = {
        "original" : {
            "HLS_VIDEO_SIZE": "original",
            "HLS_VIDEO_FPS": "24",
            "HLS_VIDEO_CODEC": "copy",
            "HLS_AUDIO_CODEC": "copy",
            "HLS_AUDIO_BITRATE": "128"
            },
        "FHD" : {
            "HLS_VIDEO_SIZE": "1920x1080",
            "HLS_VIDEO_FPS": "24",
            "HLS_VIDEO_CODEC": "libx264",
            "HLS_AUDIO_CODEC": "aac",
            "HLS_AUDIO_BITRATE": "128"
            },
        "HD" : {
            "HLS_VIDEO_SIZE": "1280x720",
            "HLS_VIDEO_FPS": "24",
            "HLS_VIDEO_CODEC": "libx264",
            "HLS_AUDIO_CODEC": "aac",
            "HLS_AUDIO_BITRATE": "128"
            },
        "SD" : {
            "HLS_VIDEO_SIZE": "720x432",
            "HLS_VIDEO_FPS": "24",
            "HLS_VIDEO_CODEC": "libx264",
            "HLS_AUDIO_CODEC": "aac",
            "HLS_AUDIO_BITRATE": "128"
            },
        "CD" : {
            "HLS_VIDEO_SIZE": "320x240",
            "HLS_VIDEO_FPS": "24",
            "HLS_VIDEO_CODEC": "libx264",
            "HLS_AUDIO_CODEC": "aac",
            "HLS_AUDIO_BITRATE": 64000
            },
        }
