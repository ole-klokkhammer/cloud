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

echo "pgBackRest $TYPE backup completed successfully."

exit 0