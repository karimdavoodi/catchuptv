#!/bin/bash

POSITIONAL=()
while [[ $# -gt 0 ]]; do
	key="$1"
	case $key in
		-c|--channel)
			CHANNEL_NAME="$2"
			shift;shift 
			;;
		-u|--url)
			CHANNEL_URL="$2"
			shift;shift 
			;;
		-v|--video-codec)
			HLS_VIDEO_CODEC="$2"
			shift;shift 
			;;
		-s|--video-size)
			HLS_VIDEO_SIZE="$2"
			shift;shift 
			;;
		-f|--video-fps)
			HLS_VIDEO_FPS="$2"
			shift;shift 
			;;
		-b|--video-bitrate)
			HLS_VIDEO_BITRATE="$2"
			shift;shift 
			;;
		-a|--audio-codec)
			HLS_AUDIO_CODEC="$2"
			shift;shift 
			;;
		-t|--audio-bitrate)
			HLS_AUDIO_BITRATE="$2"
			shift;shift 
			;;
		*)    # unknown option
			shift # past argument
			;;
	esac
done

echo "${CHANNEL_NAME}" 
echo "${CHANNEL_URL}" 
echo "${HLS_VIDEO_CODEC}" 
echo "${HLS_VIDEO_BITRATE}"
echo "${HLS_VIDEO_SIZE}" 
echo "${HLS_VIDEO_FPS}" 
echo "${HLS_AUDIO_CODEC}" 
echo "${HLS_AUDIO_BITRATE}"

# sed 's/CHANNEL_NAME:.*/CHANNEL_NAME: "nnnn"/' chan-net-to-hls.yaml mm

