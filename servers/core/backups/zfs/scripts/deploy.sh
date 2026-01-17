#!/bin/bash

set -e
 
REMOTE_USER=ubuntu
REMOTE_HOST=core.home.lan

# Copy files to remote server
scp lib.sh sanoid.conf post_snapshot.sh pruning_script.sh restore.sh post_snapshot.env.example install-sanoid-hooks.sh ${REMOTE_USER}@${REMOTE_HOST}:/tmp/

# SSH in and run the installer
ssh -t ${REMOTE_USER}@${REMOTE_HOST} "
    cd /tmp && \
    chmod +x install-sanoid-hooks.sh && \
    sudo ./install-sanoid-hooks.sh && \
    sudo cp /tmp/sanoid.conf /etc/sanoid/sanoid.conf && \
    echo 'Updated /etc/sanoid/sanoid.conf'
"
echo "Sanoid hook scripts and config deployed to ${REMOTE_HOST}"