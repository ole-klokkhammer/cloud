# sensors

## setup
### install lm-sensors
```bash
sudo apt update
sudo apt install -y lm-sensors
```

### detect sensors
Run the detection script and accept defaults (type `YES` at the end to save to `/etc/modules`).
```bash
sudo sensors-detect
```

### load amd module
```bash
sudo modprobe k10temp
```

## usage
### check temperatures
```bash
sensors
```

### monitor in real-time
```bash
watch -n 1 sensors
```

### visual dashboard
```bash
sudo apt install -y