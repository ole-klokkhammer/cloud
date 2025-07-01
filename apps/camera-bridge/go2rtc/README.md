# go2rtc

* https://github.com/AlexxIT/go2rtc/wiki/Hardware-acceleration
* https://github.com/AlexxIT/go2rtc/tree/master/internal/app

## setup
* kubectl create namespace camera-bridge
* kubectl create secret generic -n camera-bridge  go2rtc-secrets --from-env-file=.env
* kubectl apply -f deployment.yaml
* kubectl apply -f service.yaml

## nvidia hardware 
check why frigate has support:
 V....D av1_nvenc            NVIDIA NVENC av1 encoder (codec av1)
 V....D h264_nvenc           NVIDIA NVENC H.264 encoder (codec h264)
 V....D hevc_nvenc           NVIDIA NVENC hevc encoder (codec hevc)
* /usr/lib/ffmpeg/7.0/bin/ffmpeg -hide_banner -encoders | grep NVIDIA
* /usr/lib/ffmpeg/7.0/bin/ffmpeg -hide_banner -decoders | grep NVIDIA


## reolink
https://github.com/QuantumEntangledAndy/neolink