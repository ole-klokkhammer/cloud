#!/bin/bash

set -x

echo "This script runs k3s-volume backups."

BUCKET_NAME="k3s-volumes"
AWS_PROFILE="k3s-volume-backup"
TIMESTAMP=$(date +%s)
ZFS_POOL="ssd/k3s"
SNAPSHOT_PREFIX="snapshot" 
SNAPSHOT_KEEP=7
ENDPOINT_URL="https://j8t7.ldn203.idrivee2-94.com"
HEALTHCHECKS_URL="http://healthchecks.home.lan/ping/f049b364-9bd6-4d87-b748-5876a9e297fc"
 
echo "List all ZFS volumes (zvols) and filesystems in the pool: $ZFS_POOL"
for volume in $(zfs list -H -o name -t filesystem,volume | grep "^$ZFS_POOL/"); do
  VOLUME_NAME=$volume 
  SNAPSHOT="${VOLUME_NAME}@${SNAPSHOT_PREFIX}-${TIMESTAMP}" 
  SNAPSHOT_PATH="/tmp/$(echo "${SNAPSHOT}" | tr '/:' '__').zfs"
  S3_SNAPSHOT_PATH="$(echo "${SNAPSHOT}" | tr '@' '/').zfs"

  echo "Creating snapshot: $SNAPSHOT"
  zfs_snapshot_output=$(
    zfs snapshot "$SNAPSHOT"
  )
  ZFS_SNAPSHOT_STATUS=$?
  if [ $ZFS_SNAPSHOT_STATUS -ne 0 ]; then
    echo "zfs snapshot failed"
    echo "$zfs_snapshot_output"
    curl "$HEALTHCHECKS_URL/fail"
    exit $ZFS_SNAPSHOT_STATUS
  fi

  echo "Sending snapshot to file: $SNAPSHOT_PATH"
  zfs_send_output=$(
    zfs send "$SNAPSHOT" > "$SNAPSHOT_PATH"
  )
  ZFS_SEND_STATUS=$?
  if [ $ZFS_SEND_STATUS -ne 0 ]; then
    echo "zfs send failed"
    echo "$zfs_send_output"
    curl "$HEALTHCHECKS_URL/fail"
    exit $ZFS_SEND_STATUS
  fi

  echo "Uploading $SNAPSHOT_PATH to S3"
  aws_output=$(
    aws s3api put-object \
      --bucket "$BUCKET_NAME" \
      --key "$S3_SNAPSHOT_PATH" \
      --body "$SNAPSHOT_PATH" \
      --profile "$AWS_PROFILE" \
      --endpoint-url "$ENDPOINT_URL"
  )
  AWS_STATUS=$?
  if [ $AWS_STATUS -ne 0 ]; then
    echo "aws s3 upload failed"
    echo "$aws_output"
    curl "$HEALTHCHECKS_URL/fail"
    exit $AWS_STATUS
  fi

  echo "Cleaning up local snapshot file"
  rm -f "$SNAPSHOT_PATH"

  echo "Keeping only the latest $SNAPSHOT_KEEP snapshots in S3 for this volume"
  SNAPSHOT_LIST=$(
    aws s3api list-objects-v2 \
    --bucket "$BUCKET_NAME" \
    --profile "$AWS_PROFILE" \
    --endpoint-url "$ENDPOINT_URL" \
    --query 'Contents[].Key' \
    --output json | jq -r ".[] | select(startswith(\"$VOLUME_NAME\"))" | sort -n
  )
  SNAPSHOT_COUNT=$(echo "$SNAPSHOT_LIST" | wc -l)

  echo "Found $SNAPSHOT_COUNT snapshots for $VOLUME_NAME in S3."
  if [ "$SNAPSHOT_COUNT" -gt "$SNAPSHOT_KEEP" ]; then
    SNAPSHOTS_TO_DELETE=$(echo "$SNAPSHOT_LIST" | head -n -$(($SNAPSHOT_KEEP)))
    for OLD_SNAPSHOT in $SNAPSHOTS_TO_DELETE; do
      echo "Deleting old snapshot from S3: $OLD_SNAPSHOT"
      aws_output=$(
        aws s3api delete-object \
          --bucket "$BUCKET_NAME" \
          --key "$OLD_SNAPSHOT" \
          --profile "$AWS_PROFILE" \
          --endpoint-url "$ENDPOINT_URL"
      )
      AWS_DELETE_STATUS=$?
      if [ $AWS_DELETE_STATUS -ne 0 ]; then
        echo "aws s3 delete failed for $OLD_SNAPSHOT"
        echo "$aws_output" 
      fi
    done 
  else
    echo "No snapshots to delete for volume $volume. Keeping the latest $SNAPSHOT_KEEP snapshots."
  fi

  echo "Done with volume $volume"
done

echo "All ZFS volume snapshots completed and uploaded."
curl "$HEALTHCHECKS_URL"


