# lxd 
- lxc profile create k3s
- lxc profile edit k3s
- lxc launch ubuntu:24.04 master0 -p default -p k3s
- lxc exec master0 -- bash


## notes on bind mounts
- zfs
  - bind mounts must be the same as on the host
  - use shift: "true" for easier permissions management

## how to run k3s in lxc
- ensure:
  - hostname is the same as the backup
    - sudo hostnamectl set-hostname master0
  - ensure ip is the same as restored config 
- prevent writing kernel logs
  - sudo ln -s /dev/null /dev/kmsg 
- HOST: ipvs kernel modules:
  sudo modprobe ip_vs ip_vs_rr ip_vs_wrr ip_vs_sh 
  sudo tee /etc/modules-load.d/ipvs.conf >/dev/null << 'EOF'
  ip_vs
  ip_vs_rr
  ip_vs_wrr
  ip_vs_sh
  EOF

  sudo update-initramfs -u
- LXC: set ipvs mode in k3s
  sudo mkdir -p /etc/systemd/system/k3s.service.d

  sudo tee /etc/systemd/system/k3s.service.d/10-kube-proxy.conf >/dev/null << 'EOF'
  [Service]
  Environment="K3S_KUBE_PROXY_ARGS=--proxy-mode=ipvs"
  EOF

  sudo systemctl daemon-reload
  sudo systemctl restart k3s

## temp fix for iptables on host
- HOST miti:
  sudo sysctl -w vm.overcommit_memory=1
  sudo sysctl -w kernel.panic=10
  sudo sysctl -w kernel.panic_on_oops=1

  sudo tee /etc/sysctl.d/99-k3s.conf >/dev/null << 'EOF'
  vm.overcommit_memory=1
  kernel.panic=10
  kernel.panic_on_oops=1
  EOF

  sudo sysctl --system