#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 10 15:03:52 2022

@author: stellarremnants
"""

INIT_BAUD = 230400
SERIAL_READ_TIMEOUT = 0.1

CONNECT_BYTE = b"\x11"
RESTART_BYTE = b"\xDD"
CONFIRM_BYTE = b"\xEE"
REJECT_BYTE = b"\xFF"

VAL_SEPARATOR = b"`,"
CH_SEPARATOR = b"`;"
LINE_TERMINATOR = b"\r\n"

RESTART_COUNT = 4
BYTES_PER_ULONG = 4
ULONG_ROLLOVER_VAL = (2**8)**BYTES_PER_ULONG