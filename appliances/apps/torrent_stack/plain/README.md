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
  - sh <(curl -sSf https://downloads.nordcdn.com/apps/linux/install.sh)
  - sudo usermod -aG nordvpn $USER
  - sudo ufw disable
  - sudo iptables -F
  - sudo iptables -X
  - nordvpn set killswitch on
  - nordvpn login --token ''
  - nordvpn connect 
 
## apps
### radarr
 https://wiki.servarr.com/radarr/installation/linux

- sudo groupadd media
- sudo useradd radarr  
- sudo apt install curl sqlite3
- wget --content-disposition 'http://radarr.servarr.com/v1/update/master/updatefile?os=linux&runtime=netcore&arch=x64'
- tar -xvzf Radarr*.linux*.tar.gz
- sudo mv Radarr /opt/
- sudo chown radarr:radarr -R /opt/Radarr
- cat << EOF | sudo tee /etc/systemd/system/radarr.service > /dev/null
[Unit]
Description=Radarr Daemon
After=syslog.target network.target
[Service]
User=radarr
Group=media
Type=simple

ExecStart=/opt/Radarr/Radarr -nobrowser -data=/var/lib/radarr/
TimeoutStopSec=20
KillMode=process
Restart=on-failure
[Install]
WantedBy=multi-user.target
EOF

### sonarr
https://sonarr.tv/#downloads-linux-ubuntu

- sudo groupadd media
- sudo useradd sonarr 
- curl -o install-sonarr.sh https://raw.githubusercontent.com/Sonarr/Sonarr/develop/distribution/debian/install.sh
- sudo bash install-sonarr.sh
XDG_CONFIG_HOME
### lidarr
https://wiki.servarr.com/lidarr/installation/linux

- sudo groupadd media
- sudo useradd radarr 
- sudo apt install curl mediainfo sqlite3 libchromaprint-tools
- wget --content-disposition 'http://lidarr.servarr.com/v1/update/master/updatefile?os=linux&runtime=netcore&arch=x64'
- tar -xvzf Lidarr*.linux*.tar.gz
- sudo mv Lidarr/ /opt
- sudo chown -R lidarr:media /opt/Lidarr
- cat << EOF | sudo tee /etc/systemd/system/lidarr.service > /dev/null
[Unit]
Description=Lidarr Daemon
After=syslog.target network.target
[Service]
User=lidarr
Group=media
Type=simple

ExecStart=/opt/Lidarr/Lidarr -nobrowser -data=/var/lib/lidarr/
TimeoutStopSec=20
KillMode=process
Restart=on-failure
[Install]
WantedBy=multi-user.target
EOF

### jackett
https://github.com/Jackett/Jackett

- sudo groupadd media
- sudo useradd jackett
- apt update
- apt install mono-devel ca-certificates-mono libcurl4-openssl-dev -y
- wget https://github.com/Jackett/Jackett/releases/download/v0.24.364/Jackett.Binaries.LinuxAMDx64.tar.gz
- tar -xvzf Jackett.Binaries.LinuxAMDx64.tar.gz
- sudo  ./install_service_systemd.sh
- edit to set XDG_CONFIG_HOME
  - nano /etc/systemd/system/jackett.service
  - Environment="XDG_CONFIG_HOME=/var/lib/jackett"

### jellyseerr


### qbittorrent
https://github.com/qbittorrent/qBittorrent/wiki/Installing-qBittorrent
https://github.com/qbittorrent/qBittorrent/wiki/Running-qBittorrent-without-X-server-(WebUI-only,-systemd-service-set-up,-Ubuntu-15.04-or-newer)

- sudo useradd qbittorrent
- apt update
- apt install qbittorrent-nox -y
- set data path like this: --profile="/var/lib/qbittorrent"
  - cat << EOF | sudo tee /etc/systemd/system/qbittorrent.service > /dev/null
  [Unit]
  Description=qBittorrent-nox service
  Documentation=man:qbittorrent-nox(1)
  Wants=network-online.target
  After=network-online.target nss-lookup.target

  [Service]
  # if you have systemd < 240 (Ubuntu 18.10 and earlier, for example), you probably want to use Type=simple instead
  Type=exec
  # change user as needed
  User=qbtuser
  # The -d flag should not be used in this setup
  ExecStart=/usr/bin/qbittorrent-nox --profile="/var/lib/qbittorrent"
  # uncomment this for versions of qBittorrent < 4.2.0 to set the maximum number of open files to unlimited
  #LimitNOFILE=infinity
  # uncomment this to use "Network interface" and/or "Optional IP address to bind to" options
  # without this binding will fail and qBittorrent's traffic will go through the default route
  # AmbientCapabilities=CAP_NET_RAW

  [Install]
  WantedBy=multi-user.target
  EOF