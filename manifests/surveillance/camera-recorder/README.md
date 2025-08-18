# camera-recorder
https://medium.com/@tom.humph/saving-rtsp-camera-streams-with-ffmpeg-baab7e80d767

## setup
* sudo zfs create -o quota=500G surveillance/entrance_roof
  

## API examples:

HLS/TS stream: http://192.168.1.123:1984/api/stream.m3u8?src=camera1 (H264)
HLS/fMP4 stream: http://192.168.1.123:1984/api/stream.m3u8?src=camera1&mp4 (H264, H265, AAC)