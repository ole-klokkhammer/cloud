#!/usr/bin/python3
import binascii


def hex_bytes_as_str(value: bytes) -> str:
    return binascii.b2a_hex(value).decode('utf-8', errors='ignore')
