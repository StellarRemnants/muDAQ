#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 19:37:47 2022

@author: stellarremnants
"""

from inititialize_serial import (
#     # BAUD, TIMEOUT, DEFAULT_DEV_PATH, SEND_PINS,
#     # initialize_serial_device,
#     # send_connect_byte,
#     # send_sync_byte,
    int_to_byte,
#     # hexbyte_to_int,
#     INIT_BAUD,
#     TIMEOUT,
#     UNO_ANALOG_PINS,
#     ATP_ANALOG_PINS,
#     DEFAULT_BAUD_INDEX,
#     UNO_DEFAULT_DEV_PATH,
#     ATP_DEFAULT_DEV_PATH,
    hexstr_to_int,
#     connect_serial_device,
#     send_restart_signal
    )
# from BAUDRATES import BAUDRATES

import numpy as np

WORD_DELIMITER = ";"
SEGMENT_DELIMITER = ","
LINE_TERMINATOR = "\r\n"

MAX_VOLTAGE = 2
RESOLUTION = 14
ADC_CONVERSION_CONSTANT = MAX_VOLTAGE * 2**-RESOLUTION

def remove_line_terminator(rls,
                           line_terminator=LINE_TERMINATOR,
                           ):
    lt_scrubbed_list = rls.split(line_terminator)
    if not len(lt_scrubbed_list):
        return None, "Empty return when splitting by line terminator"
    else:
        return lt_scrubbed_list[0], None
    
def read_until_sequence(dev, 
                        max_depth=100, 
                        end_symbols=[int_to_byte(rb) for rb in b"\r\n"]):
    last_symbols = [b"" for rb in end_symbols]
    for i in range(max_depth):
        rb = dev.read()
        last_symbols = [*last_symbols[1:], rb]
        # print(last_symbols, end_symbols)
        yield rb
        if last_symbols == end_symbols:
            break
    
def parse_word(word, segment_delimiter=SEGMENT_DELIMITER):
    try:
        time_hex, val_hex = word.split(segment_delimiter)
    except ValueError:
        return None, None
    else:
        time_int = hexstr_to_int(time_hex)
        val_int = hexstr_to_int(val_hex)
        if (time_int is None) or (val_int is None):
            return None, None
        else:
            return time_int, val_int

def parse_readline(rl, 
                   word_delimiter=WORD_DELIMITER,
                   segment_delimiter=SEGMENT_DELIMITER,
                   line_terminator=LINE_TERMINATOR,
                    encoding="utf-8",
                   ):
    try:
        rls = rl.decode(encoding)
    except UnicodeDecodeError:
        return None
    else:
        ltsl, error = remove_line_terminator(rls)
        for word in ltsl.split(WORD_DELIMITER):
            time_int, val_int = parse_word(word, SEGMENT_DELIMITER)
            if (time_int is None) or (val_int is None):
                continue
            else:
                yield(time_int, val_int)
    return None
    
def readline_to_list(rl, expected_length, **kwargs):
    rlist = np.asarray([*parse_readline(rl, **kwargs)])
    rlist_shape = rlist.shape
    if rlist_shape[0] != expected_length:
        return rlist, False
    elif (None in rlist):
        return rlist, False
    else:
        return rlist, True
    
def adc_to_mv(adc_val, conversion_const=ADC_CONVERSION_CONSTANT):
    return adc_val * conversion_const