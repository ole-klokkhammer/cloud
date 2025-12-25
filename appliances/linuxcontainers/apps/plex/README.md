# LXD

## plex

- lxc profile create plex
- lxc profile edit plex
- lxc launch ubuntu:24.04 plex -p default -p plex
- lxc exec plex -- bash
  - apt update
    apt install curl gnupg -y

    curl https://downloads.plex.tv/plex-keys/PlexSign.key \
    | gpg --dearmor \
    | tee /usr/share/keyrings/plex.gpg >/dev/null

    echo "deb [signed-by=/usr/share/keyrings/plex.gpg] https://downloads.plex.tv/repo/deb public main" \
    > /etc/apt/sources.list.d/plexmediaserver.list

    apt update
    apt install plexmediaserver -y

    systemctl enable plexmediaserver
    systemctl restart plexmediaserver


## file permissions
- use shift
- sudo chown -R plex:plex /var/lib/plexmediaserver
  sudo chmod -R u+rwX /var/lib/plexmediaserver
  sudo systemctl restart plexmediaserver