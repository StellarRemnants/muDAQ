#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 13:07:23 2022

@author: stellarremnants
"""

from inititialize_serial import (
    # BAUD, TIMEOUT, DEFAULT_DEV_PATH, SEND_PINS,
    # initialize_serial_device,
    # send_connect_byte,
    # send_sync_byte,
    int_to_byte,
    # hexbyte_to_int,
    INIT_BAUD,
    TIMEOUT,
    UNO_ANALOG_PINS,
    ATP_ANALOG_PINS,
    DEFAULT_BAUD_INDEX,
    UNO_DEFAULT_DEV_PATH,
    ATP_DEFAULT_DEV_PATH,
    hexstr_to_int,
    connect_serial_device,
    send_restart_signal
    )
from BAUDRATES import BAUDRATES

import numpy as np
import time

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
        
# def new_readline(dev):
#     return "".join([rb.decode("utf-8") for rb in read_until_sequence(dev)])
    
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
    
    # rls = rl.decode(encoding)
    # ltsl, error = remove_line_terminator(rl,
    #                               line_terminator=LINE_TERMINATOR,
    #                               )
    # if ltsl is None:
    #     return None
    
    # for word in ltsl.split(word_delimiter):
    #     if not len(word):
    #         continue
    #     else:
    #         time_int, val_int = parse_word(word, segment_delimiter)
    #         if (time_int is None) or (val_int is None):
    #             # continue
    #             yield time_int, val_int
    #         else:
    #             yield time_int, val_int

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

def get_timing_info(dev, 
                    max_reads, 
                    send_pins=UNO_ANALOG_PINS, 
                    verbose=False):
    # MAX_READS = 100
    
    delays_array = np.zeros(max_reads, dtype=float)
    deltas_array = np.zeros(max_reads, dtype=float)
    
    time_of_last = 0
    
    num_pins = len(send_pins)
    
    # verbose = False
    
    for i in range(max_reads):
        rl = dev.readline()
        # rl = new_readline(dev)
        rlist, success = readline_to_list(rl, num_pins)
        if not success:
            # raise Exception(f"Incorrect line: {rl}")
            i -= 1
            continue
        if rlist.shape[1] != 2:
            # raise Exception("Incorrect rlist dimensions")
            i -= 1
            continue
            # print(rlist)
        
        timestamp = rlist[0,0]
        if not (timestamp is None):
            message_delta = timestamp-time_of_last
        else:
            raise Exception(f"timestamp is None {rlist}")
        time_of_last = timestamp
        
        delays = np.asarray([0, *rlist[1:,0]])
        delay_vals = np.diff(delays)
        mean_delay = np.mean(delay_vals)
        
        delays_array[i] = mean_delay
        deltas_array[i] = message_delta
        
        if verbose:
            mvlist = adc_to_mv(rlist[:,1])
            pins_str = "PINS:  " + ", ".join([f"  {p:03d}" for p in send_pins])
            time_str = "DELAY: " + ", ".join([f"{v:05d}" for v in delays])
            val_str =  "VALUE: " + ", ".join([f"{v:05d}" for v in rlist[:,1]])
            mv_str =   "VOLTS: " + ", ".join([f"{v:05.3f}" for v in mvlist])
            print(f"TIME:    {timestamp:010d}, DELTA: {message_delta:05d}, ")
            print(pins_str)
            print(time_str)
            print(val_str)
            print(mv_str)
            print()
            if not(success):
                print("Got a line with an incorrect length!")
            
    total_mean_delay = np.mean(delays_array)
    total_mean_delta = np.mean(deltas_array[1:])
    
    if verbose:
        message_frequency = 1/(total_mean_delta * 10**-6)
        word_frequency = message_frequency*num_pins
        sample_frequency = 1/(total_mean_delay * 10**-6)
    
        print(f"S/CH/s:  {message_frequency:07.2f} [Hz]")
        print(f"S/s:     {word_frequency:07.2f} [Hz]")
        print(f"S/s/msg: {sample_frequency:07.2f} [Hz]")
        
    return total_mean_delay, total_mean_delta

# %%
if __name__ == "__main__":
    
    
    repeat_num = 5
    max_reads=25
    dots = True
    summary = True
    verbose = True
    substatus = False
    time_now = int(time.time())
    outfile = f"baudrate_analysis-{time_now}.csv"
    with open(outfile, "w") as outfilefd:
        outfilefd.write("BAUD,CH#,Ts,Ts_err,Ch,Ch_err,Dt,Dt_err,\n")
    
    # baud_range = [ 13, 17, 21, 25, 29]
    baud_range = list(range(10, 30))
    for baud_index in baud_range:
        for num_channels in range(1, len(UNO_ANALOG_PINS)+1):
        
            send_pins = UNO_ANALOG_PINS[:num_channels]
            
            baudrate = BAUDRATES[baud_index]
            dev, error = connect_serial_device(
                device_path=UNO_DEFAULT_DEV_PATH,
                initial_baudrate=INIT_BAUD,
                timeout=TIMEOUT,
                read_pins=send_pins,
                baud_index=baud_index,
                verbose=verbose,
                connect_kwags={"verbose":verbose},
                sync_kwags={"verbose":verbose},
                pin_kwags={"verbose":verbose},
                baud_kwags={"verbose":verbose},
                )
            
            if not(error is None):
                print("Failed to properly connect. Aborting...")
                raise Exception("ERROR: Failed to properly connect")
        
            
            delay_array = np.zeros(repeat_num, dtype=float)
            delta_array = np.zeros(repeat_num, dtype=float)
            for i in range(repeat_num):
                completion_fraction = (i+1)/(repeat_num)
                # print(f"Run {i+1}/{repeat_num} ({completion_fraction:04.1%})")
                if dots:
                    print(".", end="")
                delay_array[i], delta_array[i] = get_timing_info(
                    dev, 
                    max_reads=max_reads, 
                    send_pins=send_pins, 
                    verbose=substatus)
            if dots:
                print()
            NUM_PINS = len(send_pins)
            if np.sum(delay_array):
                total_mean_delay = np.mean(delay_array)
            else:
                print("No data recorded. Continuing...")
                continue
            if np.sum(delta_array):
                total_mean_delta = np.mean(delta_array[1:])
            else:
                print("No data recorded. Continuing...")
                continue
            
            msg_freq = delta_array**-1 * 10**6
            ch_freq = msg_freq * NUM_PINS
            max_freq = delay_array**-1 * 10**6
            
            message_frequency = np.mean(msg_freq)
            channel_frequency = np.mean(ch_freq)
            sample_frequency = np.mean(max_freq)
            
            root_n_inv = NUM_PINS ** -0.5
            message_error = np.std(msg_freq) * root_n_inv; message_error_percent = message_error/message_frequency
            channel_error = np.std(ch_freq) * root_n_inv; channel_error_percent = channel_error/channel_frequency
            sample_error = np.std(max_freq) * root_n_inv; sample_error_percent = sample_error/sample_frequency
            
            message_frequency = 1/(total_mean_delta * 10**-6)
            word_frequency = message_frequency*NUM_PINS
            sample_frequency = 1/(total_mean_delay * 10**-6)
            if summary:
                print("================================")
                print(f"BAUD: {BAUDRATES[baud_index]} ({baud_index})")
                print(f"CH#:  {num_channels}")
                print(f"S/CH/s:  {message_frequency:07.2f} +- {message_error:05.3f} ({message_error_percent:4.2%}) [Hz]")
                print(f"S/s:     {channel_frequency:07.2f} +- {channel_error:05.3f} ({channel_error_percent:4.2%})[Hz]")
                print(f"S/s/msg: {sample_frequency:07.2f} +- {sample_error:05.3f} ({sample_error_percent:4.2%})[Hz]")
                print("================================")
            data_line = (
                f"{baudrate},{num_channels},"
                f"{message_frequency:.2f},{message_error:.3f},"
                f"{channel_frequency:.2f},{channel_error:.3f},"
                f"{sample_frequency:.2f},{sample_error:.3f},"
                )
            # print(data_line)
            with open(outfile, "a") as outfilefd:
                outfilefd.write(data_line)
                outfilefd.write("\n")
            
            send_restart_signal(dev, verbose=verbose)
            # send_restart_signal(dev, verbose=verbose)
            time.sleep(1)
            
            dev.baudrate = INIT_BAUD