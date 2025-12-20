#!/bin/bash

# Determine backup type: full on Sunday, incr otherwise
if [ "$(date +%u)" -eq 7 ]; then
  TYPE="full"
else
  TYPE="incr"
fi

pgbackrest --stanza=main --log-level-console=info --type="$TYPE" backup
PG_STATUS=$?
if [ $PG_STATUS -ne 0 ]; then
  echo "pgBackRest $TYPE backup failed"
  exit $PG_STATUS
fi

echo "Notify healthchecks on success"
curl -fsS http://healthchecks.home.lan/ping/379f455d-9c14-4572-9da8-a49d86a6b7f1

echo "backup completed successfully."
exit 0