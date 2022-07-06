#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 17:32:46 2022

@author: stellarremnants
"""

import numpy as np
import pandas
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

from file_read_functions import process_data_from_path

def mix_colors(color_1_code, color_2_code="#000000", proportion=0.5):
    color_1_ints = np.asarray([int(color_1_code[1:][2*i:2*(i+1)], 16) for i in range(3)])
    color_2_ints = np.asarray([int(color_2_code[1:][2*i:2*(i+1)], 16) for i in range(3)])
    mixed_floats = color_1_ints*(1-proportion) + proportion * color_2_ints
    mixed_ceil = np.ceil(mixed_floats)
    mixed_ints = [int(i) for i in mixed_ceil]
    color_code_ret = "#"
    for i in mixed_ints:
        code_val = f"{hex(i)[2:]}"
        if len(code_val) == 1:
            code_val = "0" + code_val
        color_code_ret += code_val
    return color_code_ret

def lighten_color(color_code, proportion=0.5):
    return mix_colors(color_code, "#FFFFFF", proportion)

def darken_color(color_code, proportion=0.5):
    return mix_colors(color_code, "#000000", proportion)

if __name__ == "__main__":
    
    
    PROP_CYCLE = plt.rcParams['axes.prop_cycle']
    COLOR_CYCLE = PROP_CYCLE.by_key()['color']
    
    data_file_path = (
        "thermistor_data/thermistor_02_test_0007.csv"
        )
    
    data_dict, device_dict, start_datetime = process_data_from_path(data_file_path)
    
    
    fig, axes = plt.subplots(nrows=2)
    
    savgol_list = []
    keys_list = list(data_dict.keys())
    # keys_list = [11]
    for i in range(len(keys_list)):
        ch_id = keys_list[i]
        dataframe = data_dict[ch_id]
        
        time_array = dataframe["TIME"]
        temp_C_array = dataframe["temp_C"]
        
        dt_avg = np.mean(np.diff(time_array))*1e-6
        window_time = 0.01
        window_length = int(np.ceil(window_time/dt_avg))
        if window_length %2 == 0:
            window_length += 1
            
        polyorder = 1
        color = COLOR_CYCLE[i%len(COLOR_CYCLE)]
        dark_color = darken_color(color)
        axes[0].plot(time_array, temp_C_array, label=f"ch_id={ch_id}",
                color=color
                )
        
        y = savgol_filter(temp_C_array, window_length, polyorder)
        
        axes[0].plot(time_array, y,
                color=dark_color,
                zorder=10)
        
        fft = np.real(np.fft.rfft(temp_C_array-np.mean(temp_C_array)))
        freqs = np.fft.rfftfreq(len(temp_C_array), d=dt_avg)
        psd = fft**2
        axes[1].plot(freqs, psd, color=color)
        
        sfft = np.real(np.fft.rfft(y-np.mean(y)))
        
        spsd = sfft**2
        axes[1].plot(freqs, spsd, color=dark_color, zorder=10)
        
    axes[0].legend(loc="upper right")
    
        
        