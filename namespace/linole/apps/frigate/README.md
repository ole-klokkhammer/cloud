# frigate
- https://docs.frigate.video/frigate/installation/
- https://github.com/blakeblackshear/blakeshome-charts/tree/master/charts/frigate

## nvidia hardware acceleration
- https://docs.k3s.io/advanced
- https://docs.frigate.video/configuration/hardware_acceleration/
- https://dev.to/mweibel/add-nvidia-gpu-support-to-k3s-with-containerd-4j17

### create secret
* kubectl create secret generic -n linole  frigate-secrets --from-env-file=.env

# coral
- https://coral.ai/docs/accelerator/get-started/#requirements

# reolink
- remove timestamp and logo
- On, fluency first this sets the camera to CBR (constant bit rate)
- Interframe Space 1x this sets the iframe interval to the same as the frame rate