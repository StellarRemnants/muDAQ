#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 13:36:50 2023

@author: stellarremnants
"""


import json
import time
import datetime
import os
import numpy as np
import threading

from json_classes import program_settings
from serial_functions import (
    prepare_serial_device,
    send_connect_byte,
    send_pin_count,
    send_pins,
    send_pin_delays,
    # read_to_file_for_duration,
    send_restart_signal,
    # read_indefinite,
    # parse_readline,
    bytestring_to_int,
    dev_read_until,
    )

# =============================================================================
# General Functions
# =============================================================================
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
    send_connect_byte(dev, verbose=verbose)
    send_pin_count(dev, pins, verbose=verbose)
    send_pins(dev, pins, verbose=verbose)
    
    dev.reset_input_buffer()
    send_pin_delays(dev, pin_delays, verbose=verbose)

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
        
        
def prepare_file(data_file_path, program, verbose = True):
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
        now_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
        fdout.write(f"UTC datetime,{now_datetime.ctime()}\n")
        fdout.write(f"UTC timestamp,{now_datetime.timestamp()}\n")
        prog_json= program.to_json(indent=2)
        fdout.write("`---`,,\n")
        fdout.write(prog_json)
        fdout.write("\n")
        fdout.write("`---`,,\n")
        fdout.write("COMPTIME,DEVID,CH,TIME,ADC\n")
        

# %%

# =============================================================================
# Multi-device functions
# =============================================================================
    
def validate_device_list(program, verbose=True):
    device_list = [get_device_settings(program, device_index=i) for i in range(len(program.device_list))]
    ports = np.asarray([device.port for device in device_list])
    unique_ports = np.unique(ports)
    counts = np.asarray([ports[ports==port].size for port in unique_ports])
    duplicates = False
    for i in range(counts.size):
        if counts[i] != 1:
            duplicates = True
            if verbose:
                print(f"Duplicate port: {unique_ports[i]} ({counts[i]} found)")
    if duplicates:
        raise Exception(f"Duplicate port(s) found. Unable to safely continue. [{', '.join(unique_ports[counts > 1])}]")
        
        
    for port in unique_ports:
        if not(os.path.exists(port)):
            raise Exception(f"Port is not connected! \"{port}\"")

def allocate_data_file_path(program, verbose=True, MAX_FILE_COUNT=100000):
    data_file_prefix = program.data_file_prefix
    log_num = int(np.max([np.ceil(np.log10(MAX_FILE_COUNT)), 4]))
    valid_name = False
    for i in range(MAX_FILE_COUNT):
        data_file_path = f"{data_file_prefix}_{i:0{log_num}d}.csv"
        if os.path.exists(data_file_path):
            pass
        else:
            valid_name = True
            break
    if not(valid_name):
        raise Exception(f"Maximum number {MAX_FILE_COUNT} of similarly named files reached for data_file_prefix "
          f"\"{data_file_prefix}\". Please use a new data_file_prefix in your .json control file.")
    else:
        
        prepare_file(data_file_path, program,verbose=verbose)
        return data_file_path
    
def create_file_lock():
    file_lock = threading.Lock()
    return file_lock

## DEFINE START FUNCTION
def collection_start_fnc(data_file_path, program, verbose=True):
    
    ## LOAD DEVICES
    start_time = None
    device_list = []
    dev_args_list = []
    device_count = len(program.device_list)
    
    for i in range(device_count):
        if verbose:
            print(f"Registering device {i} ...")
        device = get_device_settings(program, device_index=i)
        device_list.append(device)
        dev, pins, pin_delays = prepare_device_for_read(device, verbose=verbose)
        dev_args_list.append([dev, pins, pin_delays])
    
    ## ANNOUNCE START CONDITIONS
    if verbose:
        for i in range(device_count):
            device = device_list[i]
            collection_mode = device.collection_mode.lower()
            if verbose:
                print(f"Dev {i:2d} -- MODE: {collection_mode} -- NAME: {device.device_name}",end="")
                if collection_mode == "duration":
                    print(f" -- DUR: {device.collection_duration}")
                else:
                    print()
    
    ## GET START TIME
    start_time = time.time()
    
    return start_time, device_list, dev_args_list, device_count

## DEFINE COLLECTION END FUNCTION
def collection_end_fnc(dev_args_list, end_array, program, verbose):
    for i in range(end_array.size):
        if verbose:
            print(f"Restarting serial device {i} ... ")
        dev, pins, pin_delays = dev_args_list[i]
        restart_device(dev, program, verbose=verbose)
        end_array[i] = False
        
    
## DEFINE READ FUNCTION
def read_from_device(dev):
    return dev_read_until(dev)


def collect_duration_condition(start_time, duration, *args, **kwargs):
    """
    Returns True to continue collection
    Returns False to stop collection
    """
    return (time.time() - start_time) < duration

def collect_indefinite_condition(*args, **kwargs):
    return True

def parse_readline(rl):
    pods = [a.split(b"`,") for a in rl.split(b"`;")][:-1]
    ret = []
    for pod in pods:
        if len(pod) != 3:
            pass
        else:
            ret.append([bytestring_to_int(a) for a in pod])
    return ret

## DEFINE THREAD FUNCTION(FILE_PATH, DEVICE, RELEVANT_ARGS)    
def thread_fnc(
        data_file_path, 
        device, 
        dev_args, 
        device_id, 
        start_array, 
        end_array, 
        start_time,
        file_lock,
        verbose=True, 
        sleep_on_empty = 0.01,
               ):
    # print(f"DEV_ARGS={dev_args}")
    dev, pins, pin_delays = dev_args
    collection_mode = device.collection_mode.lower()
    ## SETUP
    ## EXECUTION CONTINUE CONDITION
    if collection_mode == "duration":
        collection_condition = collect_duration_condition
    elif collection_mode == "indefinite":
        collection_condition = collect_indefinite_condition
    else:
        raise ValueError(f"Unrecognized collection mode: {collection_mode}")
    
    collection_kwargs = {
        "start_time": start_time,
        "duration": device.collection_duration,
        "count": device.collection_count,
        }
    
    ## WAIT TO START UNTIL ALL THREADS READY
    start_array[device_id] = 0
    if verbose:
        print(f"\tDev {device_id:2d} -- NAME: {device.device_name} -- Ready to begin collection")
        
    while np.sum(start_array):
        time.sleep(sleep_on_empty)
    
    ## WHILE CONDITION
    # print(f"collection_condition(**collection_kwargs)={collection_condition(**collection_kwargs)}")
    # print(f"end_array[device_id]={end_array[device_id]}")
    while collection_condition(**collection_kwargs) and end_array[device_id]:
        ## GET LINE FROM DEVICE
        rl = read_from_device(dev)
        # print(rl)
        comptime = time.time()
        if len(rl):
            val_list = parse_readline(rl)
            # print(f"\n{rl} <::> {val_list}")
            ## COMPUTER TIMESTAMP
            ## ACQUIRE FILE_LOCK
            file_lock.acquire()
            ## OPEN FILE APPEND
            with open(data_file_path, "a") as fdout:
            ## WRITE TO FILE
                ## "COMPTIME,DEVID,TIME,CH,ADC\n"
                for ch_int, time_int, val_int in val_list:
                    # if not (ch_int in )
                    fdout.write(
                        f"{comptime},{device_id},{ch_int},{time_int},{val_int}\n"
                        )
            ## RELEASE FILE_LOCK
            file_lock.release()
        else:
            time.sleep(sleep_on_empty)
        
    if verbose:
        print(f"DEVICE {device_id} Terminating collection")

## CREATE THREADS
def create_threads(
        data_file_path, 
        device_list, 
        dev_args_list, 
        start_array, 
        end_array, 
        start_time,
        file_lock,
        verbose=True, 
        sleep_on_empty = 0.01,):
    
    threads = []
    for i in range(len(device_list)):
        device = device_list[i]
        dev_args = dev_args_list[i]
        args = {
            "data_file_path":data_file_path, 
            "device":device, 
            "dev_args":dev_args, 
            "device_id":i, 
            "start_array":start_array, 
            "end_array":end_array, 
            "start_time":start_time,
            "verbose":verbose, 
            "sleep_on_empty":sleep_on_empty,
            "file_lock":file_lock,
            "verbose":verbose,
            }
        thread = threading.Thread(target=thread_fnc, kwargs=args)
        threads.append(thread)
    return threads

## START THREADS
def start_threads(threads):
    for thread in threads:
        thread.start()

## MONITOR THREADS
def monitor_threads(threads, end_array, verbose=True, update_interval=0.01):
    try:
        initial_time = time.time()
        threads_alive = True
        threads_total = len(threads)
        while threads_alive:
            threads_status = [thread.is_alive() for thread in threads]
            threads_alive = np.any(threads_status)
            threads_alive_count = np.sum(threads_status)
            time_elapsed = time.time()-initial_time
            if threads_alive:
                if verbose:
                    print(f"\rThreads: {threads_alive_count}/{threads_total} :: Approx. Elapsed: {time_elapsed:.0f}s     ", end="")
                time.sleep(update_interval)
            else:
                if verbose:
                    print(f"\rExecution Completed! Total Approx. Time Elapsed: {time_elapsed:.0f}s")
            
    except KeyboardInterrupt:
        if verbose:
            print("KeyboardInterrupt received. Terminating data collection ... ")
        for i in range(end_array.size):
            end_array[i] = 0
    finally:
        if verbose:
            print("Data collection terminated. Cleaning up...")
            
    

## CLEANUP
    ## UNLOAD AND RESET DEVICES