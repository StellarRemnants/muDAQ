#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 10 15:02:18 2022

@author: stellarremnants
"""
# import numpy as np
import json
import time
import datetime
import os
from json_classes import program_settings
from serial_functions import (
    prepare_serial_device,
    send_connect_byte,
    send_pin_count,
    send_pins,
    send_pin_delays,
    read_to_file_for_duration,
    send_restart_signal
    )
# %%

def get_program_settings(json_file_path):
    with open(json_file_path, "r") as fdin:
        return program_settings.from_dict(json.load(fdin))
    
def get_device_settings(program, device_index=0):
    
    list_len = len(program.device_list)
    if list_len <= device_index:
        raise ValueError(f"device_index {device_index} is outside of allowed "
                         f"list indices for length {list_len}")
    else:
        return program.device_list[device_index]

def get_pins(device):
    return [ch.pin_id for ch in device.channel_list]

def get_pin_delays(device):
    return [ch.pin_delay for ch in device.channel_list]

def prepare_device_for_read(device, verbose=True):
    pins = get_pins(device)
    pin_delays = get_pin_delays(device)
    if verbose:
        print("Registering serial device...")
    dev = prepare_serial_device(device.port)
    
    if verbose:
        print("Sending read info to device...")
    send_connect_byte(dev)
    send_pin_count(dev, pins)
    send_pins(dev, pins)
    
    dev.reset_input_buffer()
    send_pin_delays(dev, pin_delays)

    return dev, pins, pin_delays

def restart_device(dev, program, verbose=True):
    if verbose:
        print("Sending restart signal...")
    send_restart_signal(dev)
    rl = dev.readline()
    if verbose:
        print("Attempting to read until termination...")
    while len(rl):
        rl = dev.readline()
        time.sleep(program.delay_on_empty)
    if verbose:
        print("Program successfully terminated.")
        
        
def prepare_file(data_file_path, device, verbose = True):
    file_abspath = os.path.abspath(data_file_path)
    
    
    if verbose:
        print("Preparing data path")
    fn_split = os.path.abspath(file_abspath).split(os.path.sep)
    if len(fn_split) > 1:
        if verbose:
            print("Preparing data directories...")
        dir_names = fn_split[:-1]
        current_dir = ""
        for subdir in dir_names:
            current_dir = os.path.join(current_dir, subdir)
            if not len(current_dir):
                current_dir = os.path.sep
                continue
            if verbose:
                print(f"\r{current_dir}", end="")
            if not os.path.exists(current_dir):
                os.mkdir(current_dir)
        if verbose:
            print()
        file_path = os.path.join(current_dir, fn_split[-1])
    else:
        file_path = os.path.abspath(file_abspath)
    if verbose:
        print(f"Final path: \"{file_path}\"")
    
    
    with open(file_abspath, "w") as fdout:
        now_datetime = datetime.datetime.utcnow()
        fdout.write(f"UTC datetime,{now_datetime.ctime()}\n")
        fdout.write(f"UTC timestamp,{now_datetime.timestamp()}\n")
        dev_json= device.to_json(indent=2)
        fdout.write("`---`,,\n")
        fdout.write(dev_json)
        fdout.write("\n")
        # dev_dict = device.to_dict()
        # for key in dev_dict.keys():
        #     val = dev_dict[key]
        #     if type(val) is list:
        #         fdout.write(f"{key},,\n")
        #         for channel in val:
        #             channel_dict = channel.to_dict()
        #             for lkey in channel_dict.keys():
        #                 lval = channel_dict[lkey]
        #                 if lkey == "channel_name":
        #                     fdout.write(f",{lkey},{lval}\n")
        #                 else:
        #                     fdout.write(f",,{lkey},{lval}\n")
        #     else:
        #         fdout.write(f"{key},{val}\n")
                
        fdout.write("`---`,,\n")
        
def collect_for_duration_from_file(json_file_path, verbose=True):
    program = get_program_settings(json_file)
    for i in range(len(program.device_list)):
        device = get_device_settings(program, device_index=i)
        #TODO: Non-blocking read implementation for multiple devices
        #TODO: Time synchronization for multiple devices
        dev, pins, pin_delays = prepare_device_for_read(device, verbose=verbose)
        dev.reset_output_buffer()
        for i in range(10):
            rl = dev.readline()
            if len(rl):
                if verbose:
                    # print(f"Line: {rl}")
                    pass
        time.sleep(1)
        
        if verbose:
            print("Reading for duration...")
            
        data_file_prefix = device.data_file_prefix
        valid_name = False
        for i in range(10000):
            data_file_path = f"{data_file_prefix}_{i:04d}.csv"
            if os.path.exists(data_file_path):
                pass
            else:
                valid_name = True
                break
        if not(valid_name):
            if verbose:
                print("Maximum number of similarly named files reached for data_file_prefix "
                  f"\"{data_file_prefix}\". Please use a new data_file_prefix in your .json control file.")
            
        else:
            if verbose:
                print(f"Preparing file: \"{data_file_path}\"")
            prepare_file(data_file_path, device)
            if verbose:
                print("Running data collection procedure \"duration\"...")
            
            
            
            num_samples, duration, bad_line_counter = read_to_file_for_duration(dev,
                                      pins,
                                      file_name = data_file_path,
                                      target_duration = device.collection_duration,
                                      ignore_first_lines = device.ignore_first_lines,
                                      sleep_on_empty = device.delay_on_empty,
                                      verbose=verbose,
                                      )
    
            restart_device(dev, program, verbose=verbose)

# %%

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        json_file = sys.argv[1]
    else:
        json_file = "New_Thermistors_2022-06-16.json"
    
    print("========================================================")
    print("Using file: ")
    print(f"\t\"{json_file}\"")
    print("========================================================")
    collect_for_duration_from_file(json_file)