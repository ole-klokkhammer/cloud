#!/bin/bash
set -e

HEALTHCHECKS_URL="http://healthchecks.home.lan/ping/<your-sanoid-uuid>"

# run sanoid
sanoid --verbose
STATUS=$?

if [ $STATUS -eq 0 ]; then
  curl -fsS "$HEALTHCHECKS_URL" >/dev/null 2>&1 || true
else
  curl -fsS "$HEALTHCHECKS_URL/fail" >/dev/null 2>&1 || true
fi

exit $STATUS