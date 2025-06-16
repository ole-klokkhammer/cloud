#!/bin/bash

# This script runs etcd backups.

BUCKET_NAME="etcd"
TIMESTAMP=$(date +%s)
SNAPSHOT="/tmp/etcd-snapshot-$TIMESTAMP"

export ETCDCTL_API=3 
etcdctl --endpoints=http://127.0.0.1:2379 snapshot save "$SNAPSHOT"
ETCD_STATUS=$?
if [ $ETCD_STATUS -ne 0 ]; then
  echo "etcdctl snapshot failed"
  exit $ETCD_STATUS
fi

 
export AWS_PROFILE="etcd-backup"
aws s3 cp "$SNAPSHOT" s3://$BUCKET_NAME --endpoint-url https://j8t7.ldn203.idrivee2-94.com
AWS_STATUS=$?
if [ $AWS_STATUS -ne 0 ]; then
  echo "aws s3 upload failed"
  exit $AWS_STATUS
fi

rm "$SNAPSHOT"

exit 0
