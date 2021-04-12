#!/bin/bash
# https://devimages.apple.com.edgekey.net/iphone/samples/bipbop/bipbopall.m3u8
# https://cph-p2p-msl.akamaized.net/hls/live/2000341/test/master.m3u8
# https://moctobpltc-i.akamaihd.net/hls/live/571329/eight/playlist.m3u8
# http://download.tsi.telecom-paristech.fr/gpac/DASH_CONFORMANCE/TelecomParisTech/mp4-live/mp4-live-mpd-AV-NBS.mpd

if [ "$#" != "16" ]; then
    echo -e "Add new chan-net-to-hls\n"
    echo -e "Usage: $0 \n"\
            "-c|--channel           <channel_name>\n"\
            "-w|--channel-bandwith  <channel_name>\n"\
            "-u|--channel-url       <channel_url>\n"\
            "-v|--video-codec       <video_codec>\n" \
            "-s|--video-size        <video_size>\n" \
            "-f|--video-fps         <video_fps>\n" \
            "-b|--video-bitrate     <video_bitrate>\n" \
            "-a|--audio-codec       <audio_codec>\n" \
            "-t|--audio-bitrate     <audio_bitrate>\n" 
    exit 0
fi
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
		-w|--channel-bandwith)
			CHANNEL_BANDWIDTH="$2"
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
cp -f ./deployments/chan-net-to-hls.yaml /tmp/chan.yaml
sed -i "s/CHANNEL_NAME:.*/CHANNEL_NAME: \"$CHANNEL_NAME\"/" /tmp/chan.yaml 
sed -i "s/CHANNEL_BANDWIDTH:.*/CHANNEL_BANDWIDTH: \"$CHANNEL_BANDWIDTH\"/" /tmp/chan.yaml 
sed -i "s/CHANNEL_URL:.*/CHANNEL_URL: \"$CHANNEL_URL\"/" /tmp/chan.yaml 
sed -i "s/HLS_VIDEO_CODEC:.*/HLS_VIDEO_CODEC: \"$HLS_VIDEO_CODEC\"/" /tmp/chan.yaml 
sed -i "s/HLS_VIDEO_SIZE:.*/HLS_VIDEO_SIZE: \"$HLS_VIDEO_SIZE\"/" /tmp/chan.yaml 
sed -i "s/HLS_VIDEO_FPS:.*/HLS_VIDEO_FPS: \"$HLS_VIDEO_FPS\"/" /tmp/chan.yaml 
sed -i "s/HLS_VIDEO_BITRATE:.*/HLS_VIDEO_BITRATE: \"$HLS_VIDEO_BITRATE\"/" /tmp/chan.yaml 
sed -i "s/HLS_AUDIO_BITRATE:.*/HLS_AUDIO_BITRATE: \"$HLS_AUDIO_BITRATE\"/" /tmp/chan.yaml 
sed -i "s/HLS_AUDIO_CODEC:.*/HLS_AUDIO_CODEC: \"$HLS_AUDIO_CODEC\"/" /tmp/chan.yaml 
ID=`echo $CHANNEL_NAME | md5sum | cut -b-10`

sed -i "s/chan-net-to-hls-config/chan-net-to-hls-config-$ID/" /tmp/chan.yaml 
sed -i "s/chan-net-to-hls-dep/chan-net-to-hls-dep-$ID/" /tmp/chan.yaml 

kubectl apply -f /tmp/chan.yaml
