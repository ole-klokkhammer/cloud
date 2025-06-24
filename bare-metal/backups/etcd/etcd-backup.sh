#!/bin/bash

# This script runs etcd backups.

set -x

BUCKET_NAME="etcd"
AWS_PROFILE="etcd-backup"
TIMESTAMP=$(date +%s)
SNAPSHOT_PREFIX="etcd-snapshot"
SNAPSHOT_NAME="$SNAPSHOT_PREFIX-$TIMESTAMP"
SNAPSHOT_PATH="/tmp/$SNAPSHOT_NAME"
SNAPSHOT_KEEP=7
ENDPOINT_URL="https://j8t7.ldn203.idrivee2-94.com"
HEALTHCHECKS_URL="http://192.168.10.204:8000/ping/55fe5c54-ca9c-431d-84cc-824376dbe8a4"

export ETCDCTL_API=3 
etcdctl_output=$(etcdctl --endpoints=http://127.0.0.1:2379 snapshot save "$SNAPSHOT_PATH" 2>&1)
ETCD_STATUS=$?
if [ $ETCD_STATUS -ne 0 ]; then
  echo "etcdctl snapshot failed"
  echo "$etcdctl_output"
  exit $ETCD_STATUS
fi
 
# aws_output=$(aws s3 cp "$SNAPSHOT" s3://$BUCKET_NAME --profile etcd-backup --endpoint-url https://j8t7.ldn203.idrivee2-94.com 2>&1)
# force single part upload to avoid multipart issues
aws_output=$(
  aws s3api put-object \
    --bucket $BUCKET_NAME \
    --key "$SNAPSHOT_NAME" \
    --body "$SNAPSHOT_PATH" \
    --profile "$AWS_PROFILE" \
    --endpoint-url "$ENDPOINT_URL" 2>&1
)
AWS_STATUS=$?
if [ $AWS_STATUS -ne 0 ]; then
  echo "aws s3 upload failed"
  echo "$aws_output"
  exit $AWS_STATUS
fi

echo "Cleanup: keep only the latest $SNAPSHOT_KEEP snapshots in the bucket"
SNAPSHOT_LIST=$(
  aws s3api list-objects-v2 \
    --bucket $BUCKET_NAME \
    --profile "$AWS_PROFILE" \
    --endpoint-url "$ENDPOINT_URL" \
    --query 'Contents[].Key' \
    --output json | jq -r ".[] | select(startswith(\"$SNAPSHOT_PREFIX\"))" | sort -n
)
SNAPSHOT_COUNT=$(echo "$SNAPSHOT_LIST" | wc -l)

if [ "$SNAPSHOT_COUNT" -gt "$SNAPSHOT_KEEP" ]; then
  SNAPSHOTS_TO_DELETE=$(echo "$SNAPSHOT_LIST" | head -n -"$SNAPSHOT_KEEP")
  for OLD_SNAPSHOT in $SNAPSHOTS_TO_DELETE; do
    echo "Deleting old snapshot: $OLD_SNAPSHOT"
    aws s3api delete-object --bucket $BUCKET_NAME --key "$OLD_SNAPSHOT" --profile "$AWS_PROFILE" --endpoint-url "$ENDPOINT_URL"
    echo "Deleted old snapshot: $OLD_SNAPSHOT"
  done
fi
rm "$SNAPSHOT_PATH"


echo "Check if the snapshot still exists in the bucket"
aws s3api head-object --bucket "$BUCKET_NAME" --key "$SNAPSHOT_NAME" --profile "$AWS_PROFILE" --endpoint-url "$ENDPOINT_URL" > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "Snapshot $SNAPSHOT_NAME has been successfully stored in the bucket."
  curl -fsS "$HEALTHCHECKS_URL"
  echo "backup completed successfully."
  exit 0
else
  echo "Snapshot $SNAPSHOT_NAME does not exist in the bucket."
  curl -fsS "$HEALTHCHECKS_URL/fail"
  exit 1
fi



