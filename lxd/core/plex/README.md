# LXD

## plex

- lxc profile create plex
- lxc profile edit plex
- lxc launch ubuntu:24.04 plex -p default -p plex
- lxc exec plex -- bash
  - apt update
    apt install curl gnupg -y

    curl -sSO https://downloads.plex.tv/plex-keys/PlexSign.v2.key
    gpg --show-keys --with-subkey-fingerprints PlexSign.v2.key

    apt update
    apt install plexmediaserver -y

    systemctl enable plexmediaserver
    systemctl restart plexmediaserver


## file permissions
- use shift
- sudo chown -R plex:plex /var/lib/plexmediaserver
  sudo chmod -R u+rwX /var/lib/plexmediaserver
  sudo systemctl restart plexmediaserver