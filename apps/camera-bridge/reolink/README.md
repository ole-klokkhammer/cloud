#
* ffmpeg -f alsa -i default -acodec pcm_alaw -ar 8000 -ac 1 -f rtsp -rtsp_transport tcp rtsp://127.0.0.1:8554/incoming

## to file
* ffmpeg -f alsa -i default -acodec pcm_s16le -ar 8000 -ac 1 output_pcm.wav

## rtsp
* ffmpeg -f alsa -i default -acodec pcm_s16le -ar 8000 -ac 1 -f rtsp -rtsp_transport tcp rtsp://127.0.0.1:8554/incoming
* ffmpeg -f alsa -i default -acodec pcm_alaw -ar 8000 -ac 1 -f rtsp -rtsp_transport tcp rtsp://127.0.0.1:8554/incoming


## mp3 test
* ffmpeg -i https://rhasspy.github.io/piper-samples/samples/en/en_US/lessac/high/speaker_0.mp3 -f  alaw -ar 8000 -f wav - | ./neolink talk Doorbell -c config.toml --volume=1.0 -m -i "fdsrc fd=0"
*  ffmpeg -re   -i https://rhasspy.github.io/piper-samples/samples/en/en_US/lessac/high/speaker_0.mp3   -vn   -c:a pcm_alaw   -ar 8000   -ac 1   -payload_type 8   -rtsp_transport tcp   -f rtsp   rtsp://127.0.0.1:8554/incoming_talk
*  ffmpeg -re -i https://rhasspy.github.io/piper-samples/samples/en/en_US/lessac/high/speaker_0.mp3 -acodec pcm_alaw -ar 8000 -f rtsp rtsp://localhost:8554/incoming