# GPU worker

## storage
sudo zfs create -o compression=lz4 -o atime=off ssd/llm/models
sudo zfs set logbias=latency ssd/llm/models
sudo zfs set recordsize=1M  ssd/llm/models 

## setup
- lxc profile create llm
- lxc profile edit llm
- lxc launch ubuntu:24.04 llm -p default -p llm
- lxc exec llm -- bash

## NUMA testing

### memory location
sudo  numastat -p $(pidof llama-server)
watch -n 0.5 "sudo  numastat -p $(pidof llama-server)"

### CPU localization
numactl --hardware
then verify cpu number with htop

### others
- numactl --cpunodebind=0 --membind=0
- numactl --interleave=all