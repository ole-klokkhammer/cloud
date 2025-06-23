#!/bin/bash

set -e

REMOTE_USER=ubuntu
REMOTE_HOST=192.168.10.2
SERVICE_NAME="k3s-volume-backup"
REMOTE_TMP_DIR="/tmp/${SERVICE_NAME}-install"

SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
TIMER_FILE="/etc/systemd/system/${SERVICE_NAME}.timer"
SCRIPT_FILE="/usr/local/bin/${SERVICE_NAME}.sh"

LOCAL_SCRIPT_FILE="$(dirname "$0")/${SERVICE_NAME}.sh"
LOCAL_SERVICE_FILE="$(dirname "$0")/${SERVICE_NAME}.service"
LOCAL_TIMER_FILE="$(dirname "$0")/${SERVICE_NAME}.timer"

echo "Copy files to remote host "
scp "$LOCAL_SCRIPT_FILE" "$LOCAL_SERVICE_FILE" "$LOCAL_TIMER_FILE" ${REMOTE_USER}@${REMOTE_HOST}:$REMOTE_TMP_DIR/

echo "Run setup commands on remote host"
ssh -t ${REMOTE_USER}@${REMOTE_HOST} "
    sudo cp $REMOTE_TMP_DIR/$(basename $LOCAL_SCRIPT_FILE) $SCRIPT_FILE && \
    sudo chmod +x $SCRIPT_FILE && \
    sudo cp $REMOTE_TMP_DIR/$(basename $LOCAL_SERVICE_FILE) $SERVICE_FILE && \
    sudo cp $REMOTE_TMP_DIR/$(basename $LOCAL_TIMER_FILE) $TIMER_FILE && \
    sudo systemctl daemon-reload && \
    sudo systemctl enable --now ${SERVICE_NAME}.timer && \
    echo '${SERVICE_NAME} systemd service and timer installed and started.' && \
    echo 'You can check the status with: systemctl status ${SERVICE_NAME}.service' && \
    echo 'Logs can be viewed with: journalctl -u ${SERVICE_NAME}.service' && \
    echo 'Backup script is located at: $SCRIPT_FILE'  && \
    echo 'You can run the backup script manually with: sudo $SCRIPT_FILE'  && \
    echo 'Cleaning up temporary files...' && \
    rm -rf $REMOTE_TMP_DIR && \
    echo 'Cleanup complete.'
"

echo "Install complete on ${REMOTE_HOST} with ${SERVICE_NAME}"