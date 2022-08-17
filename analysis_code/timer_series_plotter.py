#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 15:05:32 2022

@author: stellarremnants
"""

from file_read_functions import process_data_from_path
import matplotlib.pyplot as plt
import numpy as np
import sys

from scipy.signal import savgol_filter

MAX_TIME = 2**32

if __name__ == "__main__":
    
    DEFAULT_FILE_PATH = ("/home/stellarremnants/muDAQ/analysis_code/"
    "thermistor_data/real_tank_test/rtks_real_0001.csv")
    argv = sys.argv
    # print(argv)
    if len(argv) < 2:
        file_path = DEFAULT_FILE_PATH
    elif len(argv) > 2:
        raise ValueError("Too many inputs. Expected exactly 1 path as input.")
    else:
        file_path = argv[1]
        
    data_dict, dev_opts, start_datetime = process_data_from_path(file_path, correct_on_sensor_id=False)
    
    channel_names = {}
    for pin_id in data_dict.keys():
        matches = []
        for ch_dict in dev_opts["channel_list"]:
            if ch_dict['pin_id'] == pin_id:
                matches.append(ch_dict["channel_name"])
                
        if len(matches) < 1:
            print(f"No matches found for channel {pin_id}")
        elif len(matches) > 1:
            print(f"Multiple matches found for channel {pin_id}")
            
        else:
            channel_names[pin_id] = matches[0]
            
            
    pin_ids = list(channel_names.keys())
    NUM_PINS = len(pin_ids)
    
# %%
    
    compressed_dict = {}
    init_time = np.min([np.min(data_dict[ch_id]["TIME"][:10]) for ch_id in pin_ids]) * 1e-6
    
    BIN_TIME = 10 #s
    for i in range(NUM_PINS):
        print(f"PIN: {i+1}/{NUM_PINS}")
        ch_id = pin_ids[i]
        dataframe = data_dict[ch_id]
        time = dataframe["TIME"] * 1e-6 - init_time
        
        rollover_cond = np.asarray([False, *(np.diff(time) < -10)])
        for j in np.arange(time.size)[rollover_cond]:
            time[j:] += MAX_TIME*1e-6
            
        mean_dt = np.mean(np.diff(time))
        counts, bins = np.histogram(time, bins=int(np.ceil((time.iloc[-1]-time.iloc[0])/BIN_TIME)))
        compressed_size = counts.size
        compressed_times = (bins[:-1]+bins[1:])/2
        compressed_temps = np.zeros(compressed_size)
        compressed_temp_errors = np.zeros(compressed_size)
        
        temp = dataframe["temp_C"]
        for j in range(compressed_size):
            print(f"\r  BIN: {j+1}/{compressed_size} ({(j+1)/compressed_size:03.1%})", end="")
            condition = np.logical_and(time >= bins[j], time < bins[j+1])
            compressed_temps[j] = np.mean(temp[condition])
            compressed_temp_errors[j] = np.std(temp[condition])/(counts[j]**0.5)
        print()
        print()
        
        compressed_dict[ch_id] = (compressed_times, compressed_temps, compressed_temp_errors)
    
    
    
    
    
    # %%
    # fig, axes = plt.subplots(nrows=NUM_PINS, sharex=True)
    fig, axes = plt.subplots(nrows=1, sharex=True)
    axes = list([axes])
    
    
    for i in range(NUM_PINS):
        print(f"PIN: {i+1}/{NUM_PINS}")
        ch_id = pin_ids[i]
        
        time, temp, temp_error = compressed_dict[ch_id]
        
        axes[0].errorbar(time, temp, yerr=temp_error, label=channel_names[ch_id],
                         ls="", marker="."
                         )
    
    axes[0].legend(loc="upper right")
    axes[0].grid()
    axes[0].set_xlabel("Time Elapsed [s]")
    axes[0].set_ylabel(r"Temperature [$^\circ$C]")
    fig.suptitle(f"New Optics Tank Test 2\n{str(start_datetime)}")
    fig.set_size_inches(np.asarray([1920, 1080])/fig.dpi)
    plt.show()