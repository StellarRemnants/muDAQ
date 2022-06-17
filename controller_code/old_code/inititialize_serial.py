#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 12:46:40 2022

@author: stellarremnants
"""

import serial
import time
import numpy as np
from ATP_PIN_CONSTANTS import (A11, A12, A13, A16, A29, A31, A32, A33, A34, A35)
from UNO_PIN_CONSTANTS import (A0, A1, A2, A3, A4, A5)
from BAUDRATES import BAUDRATES

dev_num = 0
UNO_DEFAULT_DEV_PATH = f"/dev/ttyACM{dev_num}"
UNO_ANALOG_PINS = np.asarray([A0, A1, A2, A3, A4, A5], dtype=int)
ATP_DEFAULT_DEV_PATH = f"/dev/ttyUSB{dev_num}"
ATP_ANALOG_PINS = np.asarray([A11, A12, A13, A16, A29, A31, A32, A33, A34, A35], dtype=int)
    
data_log_csv = f"data_log_{dev_num}.csv"
INIT_BAUD = 230400

DEFAULT_BAUD_INDEX = 17 # 17 -> 230400
DELAY = 0.01
TIMEOUT=0.02

IGNORE_FIRST = 20
MAX_MESSAGE_CAP = 10000

MAX_READ_ATTEMPS = 100

LINE_TERMINATOR = b"\r\n"
WORD_SEPARATOR = b";"
VALUE_SEPARATOR = b","


def int_to_byte(i):
    return int(i).to_bytes(1, "big")

def hexbyte_to_int(b):
    return int(b.hex(), 16)

def hexstr_to_int(s):
    return int(s, 16)
        
def reset_dev_buffers(dev):
    dev.reset_input_buffer()
    dev.reset_output_buffer()


DEFAULT_RESTART_BYTE = int_to_byte(42)
DEFAULT_RESTART_COUNT = 4
DEFAULT_MAX_READS_TO_RESTART = 100

def initialize_serial_device(port=ATP_DEFAULT_DEV_PATH, 
                             baudrate=INIT_BAUD, 
                             timeout=TIMEOUT):
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




def read_with_max_attempts(dev, 
                           max_attempts = MAX_READ_ATTEMPS, 
                           verbose = False, 
                           status = False):
    """
    Attempt to read a bit from the device. On a timeout (empty byte string
    returned) retry the read, up to <max_attempts> number of times.

    Parameters
    ----------
    dev : serial.Serial
        Serial device handle.
    max_attempts : int, optional
        Maximum number of read attempts before exiting. The default is MAX_READ_ATTEMPS.
    verbose : bool, optional
        Print messages received or when max reads exceeded. The default is False.
    status : bool, optional
        Print a "." every 5 tries. The default is False.

    Returns
    -------
    s : TYPE
        DESCRIPTION.

    """
    fail_count = 0
    last_print = -5
    s = b""
    while s == b"":
        s = dev.read(1)
        fail_count += 1
        if fail_count > max_attempts:
            if verbose:
                print(f"Exceeded max read attempts (>{MAX_READ_ATTEMPS})!")
            break
        else:
            if fail_count - last_print >= 5 and status:
                print(".", end="")
                last_print = fail_count
            # time.sleep(DELAY)
    if verbose:
        print(f"Received non-empty reply: {s} ({hexbyte_to_int(s)})")
    return s

# # %%
# ## Initialize Connection
def send_connect_byte(dev, 
                      verbose=True,
                      substatus=False,
                      reset_buffers=True,
                      connect_byte=b"\xFF",
                      ):
    """
    Send a byte to the device to confirm the connection. Useful for preventing
    over-eager initiation of the initialization loop.

    Parameters
    ----------
    dev : serial.Serial
        Serial device handle.
    verbose : bool, optional
        Print messages to console. The default is True.
    substatus : bool, optional
        Have subcommands print their verbose messages. The default is False.
    reset_buffers : bool, optional
        Option to reset buffers after read attempt. The default is True.
    connect_byte : bytes, optional
        Byte string to send as connection byte. The default is b"\xFF".

    Returns
    -------
    s : bytestring
        Bytestring received as a reply. Reply should be b"\xFF". Empty string
        indicates no reply.

    """
    if verbose:
        print("Sending connect byte")
    dev.write(connect_byte)
    s = read_with_max_attempts(dev, verbose=substatus)
    if verbose:
        print(f"Connect response: {s}")
    if reset_buffers:
        dev.reset_input_buffer()
        dev.reset_output_buffer()
    return True, None
        

def send_pin_info(dev, 
                  send_pins,
                  maximum_sync_attempts = 100,
                  verbose = True,
                  substatus = False,
                  ):
    for pin in send_pins:
        success = False
        sync_attempt_counter = 0
        while not success and sync_attempt_counter < maximum_sync_attempts:
            dev.write(int(pin).to_bytes(1, "big"))
            s = read_with_max_attempts(dev, verbose=substatus)
            s_int = hexbyte_to_int(s)
            if s_int != pin:
                if verbose:
                    print(f"Incorrect response for pin {pin}, \"{s_int}\"")
                sync_attempt_counter += 1
                continue
            else:
                if verbose:
                    print(f"Set pin {pin}")
                success = True
        if not success:
            return False, f"Exceeded maximum sync attempts on pin {pin}"
    return True, None

def send_sync_byte(dev,
                   send_pins,
                   verbose=True,
                   substatus=False,
                   sync_byte = b"\x01",
                   maximum_sync_attempts = 100,
                   ):
    """
    

    Parameters
    ----------
    dev : serial.Serial
        Serial device handle.
    verbose : bool, optional
        Print messages to console. The default is True.
    substatus : bool, optional
        Have subcommands print their verbose messages. The default is False.
    sync_byte : bytestring, optional
        Byte device is expecting to initiate syncing. The default is b"\x01".
    maximum_sync_attempts : int, optional
        Maximum number of attempts to send any one pin. The default is 100.

    Returns
    -------
    bool
        Indicates whether sync succeeded (True) or failed (False).
    str
        Error message in the case that sync failed, None for success.

    """
    if verbose:
        print("Sending sync byte")
    reset_dev_buffers(dev)
    dev.write(sync_byte)
    s = b""
    num_pins = len(send_pins)
    s = read_with_max_attempts(dev, verbose=substatus)
    if s != b"\x00":
        if verbose:
            print(f"Failed to establish sync: ({s} != \x00)")
        return False, f"Failed to establish sync ({s} != \x00)"
    else:
        if verbose:
            print("Successfully established sync")
        itb = int_to_byte(num_pins)
        if verbose:
            print(f"Sending pin count: {itb} ({num_pins})")
        dev.write(itb)
        s = read_with_max_attempts(dev, verbose=substatus)
        if len(s):
            ret_num = hexbyte_to_int(s)
            if verbose:
                print(f"Received reply: {s} ({ret_num})")
            if ret_num != num_pins:
                if verbose:
                    print(f"ERROR, return {ret_num} != sent {num_pins}")
                return False, "Failed to set pin count: incorrect response"
            else:
                if verbose:
                    print("Sucessfuly initialized pin array")                
                
                return True, None
        else:
            if verbose:
                print("Failed to received confirmation of number of pins")
            return False, "Failed to set pin count: no response"
            
def send_baud(dev, baud_index=DEFAULT_BAUD_INDEX, verbose=True, max_attempts=100):
    rb = b""
    attempt_counter = 0
    while True:
        dev.write(int_to_byte(baud_index))
        rb = read_with_max_attempts(dev)
        if hexbyte_to_int(rb) == baud_index:
            new_baud = BAUDRATES[baud_index]
            if verbose:
                print(f"Received correct reply to set BAUD to {new_baud} (index:{baud_index})")
            dev.close()
            dev.baudrate = new_baud
            dev.open()
            dev.reset_input_buffer()
            dev.reset_output_buffer()
            time.sleep(1)
            dev.write(int_to_byte(baud_index))
            dev.readline()
            if verbose:
                print("Set new baud rate")
            return True, None
        else:
            attempt_counter += 1
            if attempt_counter >= max_attempts:
                return False, "Exceeded max attempts while trying to set baudrate"


def send_restart_signal(
        dev,
        restart_count = DEFAULT_RESTART_COUNT,
        restart_byte = DEFAULT_RESTART_BYTE,
        max_reads_to_restart = DEFAULT_MAX_READS_TO_RESTART,
        default_baudrate = INIT_BAUD,
        verbose=False
                        ):
    
    reset_dev_buffers(dev)
    first = True
    for i in range(restart_count):
        if verbose:
            print(f"Sending restart signal {i+1}/{restart_count}: {hexbyte_to_int(restart_byte)}")
        if first:
            reset_dev_buffers(dev)
            first = False
        dev.write(restart_byte)
        # rtb = read_with_max_attempts()
        
        incorrect_replies = 0;
        empty_replies = 0;
        for j in range(max_reads_to_restart):
            rtb = dev.read()
            if rtb == restart_byte:
                if verbose:
                    print(f"Got correct reply: {rtb}")
                break
            elif len(rtb):
                incorrect_replies += 1
            else:
                empty_replies += 1
        if incorrect_replies >  0:
            if verbose:
                print(f"Got {incorrect_replies} incorrect replies.")
        if empty_replies >  0:
            if verbose:
                print(f"Got {empty_replies} empty replies.")
                
        
        reset_dev_buffers(dev)
        
        
def connect_serial_device(
        device_path=UNO_DEFAULT_DEV_PATH,
        initial_baudrate=INIT_BAUD,
        timeout=TIMEOUT,
        read_pins=UNO_ANALOG_PINS,
        baud_index=DEFAULT_BAUD_INDEX,
        verbose=True,
        connect_kwags={},
        sync_kwags={},
        pin_kwags={},
        baud_kwags={},
        ):
    if verbose:
        print(f"Connecting to serial device at {device_path}")
    dev = initialize_serial_device(
        port=device_path, 
        baudrate=initial_baudrate, 
        timeout=timeout)
    dev.close()
    dev.open()
    reset_dev_buffers(dev)
    
    success, error = send_connect_byte(dev, **connect_kwags)
    if not success:
        if verbose:
            print("Failed to connect to device. Error:")
            print(f"\t{error}")
            # dev.close()
        return dev, error
    success, error = send_sync_byte(dev, read_pins, **sync_kwags)
    if not success:
        if verbose:
            print("Failed to connect to device. Error:")
            print(f"\t{error}")
            # dev.close()
        return dev, error
    success, error = send_pin_info(dev, read_pins, **pin_kwags)
    if not success:
        if verbose:
            print("Failed to connect to device. Error:")
            print(f"\t{error}")
            # dev.close()
        return dev, error
    success, error = send_baud(dev, baud_index=baud_index, **baud_kwags)
    if not success:
        if verbose:
            print("Failed to connect to device. Error:")
            print(f"\t{error}")
        return dev, error
    if verbose:
        print(f"Connected to serial device at {device_path}")
    
    return dev, None
        
        
# %%
if __name__ == "__main__": 
    
    dev, error = connect_serial_device()
    
