#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 10 15:03:37 2022

@author: stellarremnants
"""

import serial
import numpy as np
import time
import os

from global_constants import (
    INIT_BAUD,
    SERIAL_READ_TIMEOUT,
    CONNECT_BYTE,
    RESTART_BYTE,
    CONFIRM_BYTE,
    REJECT_BYTE,
    RESTART_COUNT,
    BYTES_PER_ULONG,
    VAL_SEPARATOR,
    CH_SEPARATOR,
    LINE_TERMINATOR,
    )

def int_to_single_byte(convert_int):
    if not(type(convert_int) is int):
        raise ValueError(f"Input ({convert_int}) is not an int!")
    else:
        if convert_int > 255:
            raise ValueError("Input integer is too large to be cast "
                             f"as single byte ({convert_int} > 255).")
        elif convert_int < 0:
            raise ValueError("Input integer cannot be cast as a single byte:"
                             f"is negative ({convert_int} < 0).")
        else:
            return convert_int.to_bytes(1, "big")
        
def single_byte_to_int(convert_byte):
    if not(type(convert_byte) is bytes):
        raise ValueError(f"Input ({convert_byte}) is not bytes")
    else:
        convert_hex = convert_byte.hex()
        if len(convert_hex) != 2:
            raise ValueError(f"hex representation of ({convert_byte}) has too many "
                             "characters for a single byte ({convert_hex})")
        else:
            return int(convert_hex, 16)

bytes_conversion = 1/np.log(256)
def num_bytes_for_int(convert_int):
    return (int)(np.ceil(np.log(convert_int) * bytes_conversion))

def int_to_bytestring(convert_int, ending="big", num_bytes=None):
    if not(type(convert_int) is int):
        raise ValueError(f"Input ({convert_int}) is not an int!")
    else:
        if convert_int < 0:
            raise ValueError("Input integer cannot be cast as a single byte:"
                             f"is negative ({convert_int} < 0).")
        else:
            if num_bytes is None:
                num_bytes = num_bytes_for_int(convert_int)
            return convert_int.to_bytes(num_bytes, ending)

def bytestring_to_int(convert_bytestring, big_endian=True):
    if not(big_endian):
        use_bytestring = convert_bytestring[::-1]
    else:
        use_bytestring = convert_bytestring
    
    use_hexstring = use_bytestring.hex()
    return int(use_hexstring, 16)

def hexstring_to_int(convert_hexstring, big_endian=True):
    if not(big_endian):
        raise NotImplementedError("little_endian decoding not yet implemented for hexstring conversion")
    else:
        use_hexstring = convert_hexstring
        
        return int(use_hexstring, 16)
    

def initialize_serial_device(port, 
                             baudrate=INIT_BAUD, 
                             timeout=SERIAL_READ_TIMEOUT):
    """
    Initialize the serial device with specified parameters.

    Parameters
    ----------
    port : str, optional
        Device path for arduino serial device. The default is DEFAULT_DEV_PATH.
    baudrate : int, optional
        Bitrate for connection. The default is BAUD.
    timeout : float, optional
        Timeout for read to prevent blocking. The default is TIMEOUT.

    Returns
    -------
    dev : serial.Serial
        The serial device handle.

    """
    dev = serial.Serial(
        port = port,
        baudrate = baudrate,
        )
    
    dev.timeout = timeout
    
    return dev

def write_int_to_dev(dev, input_int):
    dev.write(int_to_single_byte(input_int))

    
def parse_readline(readline, 
                   val_separator=VAL_SEPARATOR,
                   ch_separator=CH_SEPARATOR, 
                   line_terminator = LINE_TERMINATOR
                   ):
    if readline[-len(line_terminator):] == line_terminator:
        cleanline = readline.rsplit(line_terminator, 1)[0]
    else:
        return []
    
    if ch_separator in cleanline:
        ch_split = cleanline.split(ch_separator)
    else:
        ch_split = [cleanline]
        
    ret_touples = []
    for ch in ch_split:
        
        if ch.count(val_separator) == 2:
            ch_b, time_b, val_b = ch.split(val_separator)
            if not (len(ch_b)):
                ch_b = b"\x00"
            if not (len(time_b)):
                time_b = b"\x00"
            if not (len(val_b)):
                val_b = b"\x00"
            # if len(time_b) and len(val_b) and len(ch_b):
            ch_int = bytestring_to_int(ch_b)
            time_int = bytestring_to_int(time_b)
            val_int = bytestring_to_int(val_b)
            ret_touples.append((ch_int, time_int, val_int))
    return ret_touples

def dev_read_until(dev, msg_terminator=LINE_TERMINATOR):
    term_len = len(msg_terminator)
    last_chars = b" "*term_len
    read_bytes = b""
    while last_chars != msg_terminator:
        read_byte = dev.read()
        if not(len(read_byte)):
            break
        last_chars = last_chars[1:] + read_byte
        read_bytes += read_byte
    return read_bytes

def prepare_serial_device(device_path,
                          reject_byte=REJECT_BYTE
                          ):
   
    dev = initialize_serial_device(device_path)
    dev.reset_input_buffer()
    dev.reset_output_buffer()
    dev.flushInput()
    dev.flushOutput()
    
    read_byte = b" "
    while len(read_byte):
        read_byte = dev.read()
    
    dev.write(reject_byte)
    dev.read()
    
    return dev

def send_connect_byte(dev,
                      connect_byte = CONNECT_BYTE,
                      confirm_byte = CONFIRM_BYTE,
                      verbose=True
                      ):
    
    read_byte = b" "
    while read_byte != confirm_byte:
        read_byte = b" "
        dev.write(connect_byte)
        while read_byte != confirm_byte and len(read_byte):
            read_byte = dev.read()
            if verbose:
                if read_byte == confirm_byte:
                    print(f"Connect response: Success ({read_byte})")
                else:
                    print(f"Connect response: Fail ({read_byte})")

def send_pin_count(dev, 
                   pins,
                   verbose=True,
                   confirm_byte = CONFIRM_BYTE,
                   ):
    read_byte = b" "
    while read_byte != confirm_byte:
        read_byte = b" "
        write_int_to_dev(dev, len(pins))
        while read_byte != confirm_byte and len(read_byte):
            read_byte = dev.read()
            if verbose:
                if read_byte == confirm_byte:
                    print(f"Pin count response: Success ({read_byte})")
                else:
                    print(f"Pin count response: Fail ({read_byte})")
    
def send_pins(dev,
              pins,
              verbose=True,
              confirm_byte = CONFIRM_BYTE,
              ):
    for i in range(len(pins)):
        read_byte = b" "
        while read_byte != confirm_byte:
            read_byte = b" "
            dev.write(int_to_single_byte(pins[i]))
            while read_byte != confirm_byte and len(read_byte):
                read_byte = dev.read()
                if verbose:
                    if read_byte == confirm_byte:
                        print(f"Pin {pins[i]}:  Success ({read_byte})")
                    else:
                        print(f"Pin {pins[i]}:  Fail ({read_byte})")

def send_pin_delays(dev,
                    pin_delays,
                    verbose=True,
                    ):
    
    for c in pin_delays:
        d = int_to_bytestring(int(c), num_bytes=BYTES_PER_ULONG)
        dev.write(d)
        if verbose:
            print(f"Pin delay {c} -> {dev_read_until(dev)}")
    
def send_restart_signal(dev,
                        restart_count = RESTART_COUNT,
                        restart_byte = RESTART_BYTE,
                        extra_count = 2
                        ):
    
    dev.reset_input_buffer()
    dev.reset_output_buffer()
    for j in range(restart_count+extra_count): # send a few extra times, just to be sure.
                                     # Extras caught by connect loop
        dev.write(restart_byte)
        dev.read()
    read_byte = b" "
    while len(read_byte):
        read_byte = dev.read()
    dev.reset_input_buffer()
    dev.reset_output_buffer()
    dev.flushInput()
    dev.flushOutput()
    
def read_to_file_for_duration(dev,
                              pins,
                              file_name = "temp_data.csv",
                              target_duration = 10,
                              ignore_first_lines = 10,
                              sleep_on_empty = 0.1,
                              verbose=True,
                              ):    
    i = 0
    bad_line_counter = 0
    dev.reset_input_buffer()
    dev.reset_output_buffer()
    dev.flushInput()
    dev.flushOutput()
    
    for j in range(ignore_first_lines):
        dev_read_until(dev)        
            
    
    start_time = time.time()
    print_every = .1
    last_print = -print_every
    with open(file_name, "a") as fdout:
        fdout.write("TIME,CH,ADC\n")
        time_now = 0
        while time_now - start_time < target_duration:
            time_now = time.time()
            elapsed = time_now - start_time
            if elapsed > last_print + print_every:
                if verbose:
                    print(f"\r{elapsed: 4.1f}s / {target_duration}s :: {i} lines :: {bad_line_counter} fails", end="", sep="")
                last_print += print_every
            rl = dev_read_until(dev)
            if len(rl):
                val_list = parse_readline(rl)
                i += 1
                # if len(val_list) != len(pins):
                bad_channels = [not(val_list[i][0] in pins) for i in range(len(val_list))]
                if np.any(bad_channels):
                    bad_line_counter += 1
                    
                    if verbose:
                        print(f"\nBad Line: {rl}")
                
                for j in range(len(val_list)):
                    if not(bad_channels[j]):
                        ch_int, time_int, adc_int = val_list[j]
                        fdout.write(f"{time_int},{ch_int},{adc_int}\n")
            else:
                time.sleep(sleep_on_empty)
    num_samples = i
    end_time = time.time()
    duration = end_time-start_time
    if verbose:
        print()
    return num_samples, duration, bad_line_counter

def display_timing_data(duration, num_samples, bad_line_counter, pins):
    
    dur_per_line = duration/num_samples
    dur_per_sample = dur_per_line/len(pins)
    
    line_frequency = 1/dur_per_line
    sample_frequency = 1/dur_per_sample
    
    print(f"line_frequency   = {line_frequency:.2f} Hz")
    print(f"sample_frequency = {sample_frequency:.2f} Hz")
    
    fail_rate = bad_line_counter/num_samples
    print(f"fail_rate        = {fail_rate:.2%}")
    
# %%
if __name__ == "__main__":
    # pins = [14, 15, 16, 17, 18, 19]
    # pins = [14, 19]
    # pins = [14]
    # pins = [33,34,35]
    # pins = [33]
    pins = [11, 34]
    sample_frequency = 2000
    target_duration = 30
    ignore_first_lines = 10
    sleep_on_empty = 0.1
    file_name = "real_data_01.csv"
    dev_path = "/dev/ttyUSB0"
    # dev_path = "/dev/ttyACM2"
    pin_delays = np.ones_like(pins) * int(1/sample_frequency* 10**6)
    
    # %%
    dev = prepare_serial_device(dev_path)
    send_connect_byte(dev)
    send_pin_count(dev, pins)
    send_pins(dev, pins)
    # %%
    dev.reset_input_buffer()
    send_pin_delays(dev, pin_delays)
       
     # %%
    num_samples, duration, bad_line_counter = read_to_file_for_duration(dev,
                                  pins,
                                  file_name = file_name,
                                  target_duration = target_duration,
                                  ignore_first_lines = ignore_first_lines,
                                  sleep_on_empty = sleep_on_empty,
                                  verbose=True,
                                  )

    display_timing_data(duration, num_samples, bad_line_counter, pins)
    # %%
    send_restart_signal(dev)