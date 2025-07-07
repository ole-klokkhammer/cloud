#!/bin/bash

set -e

# Render TOML from template
envsubst < /config/neolink/neolink.toml.template > /config/neolink/neolink.toml
envsubst < /config/go2rtc/go2rtc.yaml.template > /config/go2rtc/go2rtc.yaml

# Run the main process
exec "$@"