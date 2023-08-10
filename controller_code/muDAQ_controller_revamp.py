#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 10 15:02:18 2022

@author: stellarremnants
"""
# import numpy as np
# %%
import numpy as np
from muDAQ_controller_functions import (
    get_program_settings,
    validate_device_list,
    allocate_data_file_path,
    collection_start_fnc,
    create_file_lock,
    create_threads,
    start_threads,
    monitor_threads,
    collection_end_fnc,
    )

#%%

if __name__ == "__main__":
    # import sys
    # if len(sys.argv) >= 2:
    #     json_file = sys.argv[1]
    # else:
    #     json_file = "multi_device_test.json"
    
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file_path")
    parser.add_argument("-v", action="count", dest="verbose")
    
    args = parser.parse_args()
    
    json_file = args.json_file_path
    verbose = args.verbose
    
    print("========================================================")
    print("Using file: ")
    print(f"\t\"{json_file}\"")
    print("========================================================")
    # collect_data_according_to_file(json_file)
    # verbose = True
    # json_file = "/home/stellarremnants/muDAQ/controller_code/multi_device_test.json"
    
    ## GET DATA FROM JSON
    program = get_program_settings(json_file)
    validate_device_list(program)
    data_file_path = allocate_data_file_path(program, verbose=verbose)
    
    start_time, device_list, dev_args_list, device_count = collection_start_fnc(
        data_file_path, program, verbose=verbose
        )
    
    file_lock = create_file_lock()
    start_array = np.ones(device_count)
    end_array = np.ones(device_count)
    
    threads = create_threads(data_file_path, 
                              device_list, 
                              dev_args_list, 
                              start_array, 
                              end_array, 
                              start_time,
                              file_lock,
                              )
    start_threads(threads)
    monitor_threads(threads, end_array)
    collection_end_fnc(dev_args_list, end_array, program, verbose)
    
# %%

# def read_to_file_for_duration(dev,
#                               pins,
#                               file_name = "temp_data.csv",
#                               target_duration = 10,
#                               ignore_first_lines = 10,
#                               sleep_on_empty = 0.1,
#                               verbose=True,
#                               ):    
#     i = 0
#     bad_line_counter = 0
#     dev.reset_input_buffer()
#     dev.reset_output_buffer()
#     dev.flushInput()
#     dev.flushOutput()
    
#     for j in range(ignore_first_lines):
#         dev_read_until(dev)        
            
    
#     start_time = time.time()
#     print_every = .1
#     last_print = -print_every
#     with open(file_name, "a") as fdout:
#         fdout.write("TIME,CH,ADC\n")
#     time_now = 0
#     try:
#         while time_now - start_time < target_duration:
#             time_now = time.time()
#             elapsed = time_now - start_time
#             if elapsed > last_print + print_every:
#                 if verbose:
#                     print(f"\r{elapsed: 4.1f}s / {target_duration}s :: {i} lines :: {bad_line_counter} fails", end="", sep="")
#                 last_print += print_every
#             rl = dev_read_until(dev)
#             if len(rl):
#                 val_list = parse_readline(rl)
#                 i += 1
#                 # if len(val_list) != len(pins):
#                 bad_channels = [not(val_list[i][0] in pins) for i in range(len(val_list))]
#                 if np.any(bad_channels):
#                     bad_line_counter += 1
                    
#                     if verbose:
#                         print(f"\nBad Line: {rl}")
                
#                 for j in range(len(val_list)):
#                     if not(bad_channels[j]):
#                         ch_int, time_int, adc_int = val_list[j]
#                         with open(file_name, "a") as fdout:
#                             fdout.write(f"{time_int},{ch_int},{adc_int}\n")
#             else:
#                 time.sleep(sleep_on_empty)
#     except KeyboardInterrupt:
#         if verbose:
#             print()
#             print("Terminated early due to keyboard interrupt.")
#     num_samples = i
#     end_time = time.time()
#     duration = end_time-start_time
#     if verbose:
#         print()
#     return num_samples, duration, bad_line_counter

# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) >= 2:
#         json_file = sys.argv[1]
#     else:
#         json_file = "multi_device_test.json"
    
#     print("========================================================")
#     print("Using file: ")
#     print(f"\t\"{json_file}\"")
#     print("========================================================")
#     collect_data_according_to_file(json_file)
