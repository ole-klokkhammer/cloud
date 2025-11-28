# LXD

## caveats
we need kernel modules for vpn, but load them read only, and with a different mount inside the lxc to avoid symlink loops:

lib-modules:
  path: /mnt/lib_modules
  source: /lib/modules
  type: disk
  readonly: "true"

## torrent

- lxc profile create torrent-stack
- lxc profile edit torrent-stack
- lxc launch ubuntu:24.04 torrent-stack -p default -p torrent-stack
- lxc exec torrent-stack -- bash
  - sudo apt update
  - sudo apt install docker.io -y
  - sudo apt update
    sudo apt install ca-certificates curl gnupg -y
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install docker-compose-plugin -y