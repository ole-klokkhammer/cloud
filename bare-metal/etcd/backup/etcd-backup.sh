#!/bin/bash

# This script runs etcd backups.

set -x

BUCKET_NAME="etcd"
TIMESTAMP=$(date +%s)
SNAPSHOT="/tmp/etcd-snapshot-$TIMESTAMP"
ENDPOINT_URL="https://j8t7.ldn203.idrivee2-94.com"

export ETCDCTL_API=3 
etcdctl_output=$(etcdctl --endpoints=http://127.0.0.1:2379 snapshot save "$SNAPSHOT" 2>&1)
ETCD_STATUS=$?
if [ $ETCD_STATUS -ne 0 ]; then
  echo "etcdctl snapshot failed"
  echo "$etcdctl_output"
  exit $ETCD_STATUS
fi
 
# aws_output=$(aws s3 cp "$SNAPSHOT" s3://$BUCKET_NAME --profile etcd-backup --endpoint-url https://j8t7.ldn203.idrivee2-94.com 2>&1)
# force single part upload to avoid multipart issues
aws_output=$(aws s3api put-object --bucket $BUCKET_NAME --key $(basename "$SNAPSHOT") --body "$SNAPSHOT" --profile etcd-backup --endpoint-url "$ENDPOINT_URL" 2>&1)
AWS_STATUS=$?
if [ $AWS_STATUS -ne 0 ]; then
  echo "aws s3 upload failed"
  echo "$aws_output"
  exit $AWS_STATUS
fi

rm "$SNAPSHOT"

echo "Notify healthchecks on success"
curl -fsS http://192.168.10.204:8000/ping/55fe5c54-ca9c-431d-84cc-824376dbe8a4


echo "backup completed successfully."
exit 0
