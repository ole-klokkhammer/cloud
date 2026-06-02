# hermes Appliance

The orchestrator and tool-execution layer.

- **Hardware:** CPU 
- **Engine:** Hermes-Agent
- **Role:** Tool coordination and state management.


## setup

### Disk
sudo zfs create \
  -o compression=lz4 \
  -o atime=off \
  -o xattr=sa \
  -o acltype=posixacl \
  -o recordsize=16K \
  ssd/appdata/hermes

### lxc
- lxc profile create hermes
- lxc profile edit hermes
- lxc launch ubuntu:24.04 hermes -p default -p hermes
- lxc exec hermes -- bash 

### hermes
https://hermes-agent.nousresearch.com/docs/getting-started/installation

curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash