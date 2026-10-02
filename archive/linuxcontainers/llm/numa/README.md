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