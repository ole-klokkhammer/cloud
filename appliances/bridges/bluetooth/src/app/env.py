#!/usr/bin/python3
import os

log_level = os.getenv("LOG_LEVEL")
connect_timeout = float(os.getenv("CONNECT_TIMEOUT", 60))
command_timeout = float(os.getenv("COMMAND_TIMEOUT", 60))