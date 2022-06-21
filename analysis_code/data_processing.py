#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 11:41:56 2022

@author: stellarremnants
"""

import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

from file_read_functions import process_data_from_path

PROP_CYCLE = plt.rcParams['axes.prop_cycle']
COLOR_CYCLE = PROP_CYCLE.by_key()['color']


def savgol_smooth_fraction(x, window_fraction, polyorder):
    window_length = int(np.ceil(x.size/window_fraction))
    return savgol_filter(x, window_length, polyorder)

def savgol_smooth_time(x, t, window_time, polyorder):
    sample_spacing = abs(np.mean(np.diff(t)))
    window_length = int(np.ceil(window_time/sample_spacing))
    if window_length % 2 == 0:
        window_length += 1
    
    return savgol_filter(x, window_length, polyorder)

def plot_time_series(ax, data_dict, ch_id, y_key="temp_C", time_offset=0, **kwargs):
    x_data = (data_dict[ch_id]["TIME"]-time_offset)*1e-6
    y_data = data_dict[ch_id][y_key]
    
    ax.plot(x_data, y_data, **kwargs)
    
def plot_fft(ax, data_dict, ch_id, y_key="temp_C", 
             power=True, remove_mean=True, normalize_output=True,
             **kwargs):
    time_data = data_dict[ch_id]["TIME"]*1e-6
    signal_data = data_dict[ch_id][y_key]
    
    if remove_mean:
        signal_data = signal_data - np.mean(signal_data)
    
    sample_spacing = abs(np.mean(np.diff(time_data)))
    fft_data = np.real(np.fft.rfft(signal_data))
    fft_freq = np.fft.rfftfreq(signal_data.size, sample_spacing)
    
    if power:
        fft_data = fft_data ** 2
        
    if normalize_output:
        fft_data = fft_data/np.max(fft_data)

    ax.plot(fft_freq, fft_data, **kwargs)
    
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

def get_time_and_savgol(data_dict,
                        y_key,
                        savgol_time_window = 0.1,
                        poly_order = 1,
                        time_offset_index_range = [0,10],
                        time_to_seconds_factor = 1e-6,
                        data_dict_time_key = "TIME",
                        ):
    savgol_dict = {}
    time_s_dict = {}
    key_list = list(data_dict.keys())
    time_offset = np.min([data_dict[i][data_dict_time_key][
        time_offset_index_range[0]:time_offset_index_range[1]
        ] for i in data_dict.keys()])
    for i in range(len(key_list)):
        ch_id = key_list[i]
        x_data = (data_dict[ch_id][data_dict_time_key]-time_offset)*time_to_seconds_factor
        time_s_dict[ch_id] = x_data
        y_data = savgol_smooth_time(data_dict[ch_id][y_key], x_data, savgol_time_window, poly_order)
        savgol_dict[ch_id] = y_data
    
    return savgol_dict, time_s_dict
    
def paired_time_series_fft_plot(data_dict, y_key="temp_C", 
                                use_time_offset=True, identifier=None, 
                                verbose=False, **kwargs):
    
    if y_key == "temp_C":
        time_y_label = r"Temperature [$^\circ$C]"
        fft_ylabel = r"Power [$^\circ$C$^2$/Hz]"
    elif y_key == "voltage":
        time_y_label = r"Voltage [V]"
        fft_ylabel = r"Power [V$^2$/Hz]"
    elif y_key == "ADC":
        time_y_label = r"ADC [arb]"
        fft_ylabel = r"Power [ADC$^2$/Hz]"
    elif y_key == "resistance":
        time_y_label = r"Resistance [$\Omega$]"
        fft_ylabel = r"Power [$\Omega$$^2$/Hz]"
    else:
        time_y_label = r"Unknown"
        fft_ylabel = r"Unknown"
        
    
    fig, axes = plt.subplots(nrows=2, sharex=False)
    
    if use_time_offset:
       time_offset = np.min([data_dict[i]["TIME"][0:10] for i in data_dict.keys()])
    else:
        time_offset = 0
    key_list = list(data_dict.keys())
    for i in  range(len(key_list)):
        ch_id = key_list[i]
        color = COLOR_CYCLE[i%len(COLOR_CYCLE)]
        plot_time_series(axes[0], data_dict, ch_id, y_key=y_key,
                         time_offset = time_offset,
                         marker=".", ms=3,
                         label=f"CH: {ch_id}",
                         color = color,
                         **kwargs
                         )
        plot_fft(axes[1], data_dict, ch_id, y_key=y_key,
                 normalize_output=False,
                marker=".", ms=3,
                label=f"CH: {ch_id}",
                color = color,
                **kwargs
                )
        
        
    savgol_dict, time_s_dict = get_time_and_savgol(data_dict, y_key)
    for i in range(len(key_list)):
        ch_id = key_list[i]
        x_data = time_s_dict[ch_id]
        y_data = savgol_dict[ch_id]
        axes[0].plot(x_data,
                     y_data,
                     lw = 1, ls="-", color=darken_color(COLOR_CYCLE[i%len(COLOR_CYCLE)]),
                     label=f"CH: {ch_id} - smoothed"
                     )
    
    axes[0].set_xlabel("Time [s]")
    axes[0].set_ylabel(time_y_label)
    axes[0].grid(which="both")
    axes[1].grid(which="both")
    axes[1].set_xlabel("Frequency [Hz]")
    axes[1].set_ylabel(fft_ylabel)
    axes[0].legend(loc="upper left")
    axes[1].legend(loc="upper right")
    suptitle_string = "Time Series and PSD"
    if not (identifier is None):
        suptitle_string = "\n".join([suptitle_string, identifier])
    if verbose:
        print(suptitle_string)
    fig.suptitle(suptitle_string)
    fig.set_size_inches(np.asarray([1920,1080])/fig.dpi)
    
    return fig, axes, savgol_dict, time_s_dict


# %%
if __name__ == "__main__":
    for i in range(10, 21):
        data_file_path = (
            "/home/stellarremnants/muDAQ/"
            f"analysis_code/thermistor_data/thermistor_test_{i:04d}.csv"
            )
        data_dict, device_dict, start_datetime = process_data_from_path(data_file_path)
        
        file_name = data_file_path.split(os.path.sep)[-1]
        
        identifier = f"\"{file_name}\"\n{start_datetime.ctime()} UTC"
        y_key = "temp_C"
        
        fig, axes, savgol_dict, time_s_dict = paired_time_series_fft_plot(data_dict, y_key=y_key, identifier=identifier)
    # plt.close(fig)
# %%
    # key_list = list(data_dict.keys())
    # fig, axes = plt.subplots(nrows=len(key_list), sharex=True, sharey=True)
    
    # frequency_label = "Frequency [Hz]"
    # time_label = "Time [s]"
    # if y_key == "temp_C":
    #     fft_ylabel = r"Temperature PSD [$^\circ$C$^2$/Hz]"
    # elif y_key == "voltage":
    #     fft_ylabel = r"Voltage PSD [V$^2$/Hz]"
    # elif y_key == "ADC":
    #     fft_ylabel = r"ADC PSD [ADC$^2$/Hz]"
    # elif y_key == "resistance":
    #     fft_ylabel = r"Resistance PSD [$\Omega$$^2$/Hz]"
    # else:
    #     fft_ylabel = r"Unknown PSD [?/Hz]"
            
    # for i in range(len(key_list)):
    #     ch_id = key_list[i]
    #     spectrum, freqs, t, im = axes[i].specgram(
    #         x = data_dict[ch_id][y_key],
    #         # x = savgol_dict[ch_id],
    #         Fs = 1/(np.mean(np.diff(time_s_dict[ch_id])))
    #         )
    #     cb = fig.colorbar(im, ax=axes[i])    
    #     axes[i].set_ylabel(frequency_label)
    #     cb.set_label(fft_ylabel)
    # axes[-1].set_xlabel(time_label)
    # plt.close(fig)
# %%
    # print([[np.mean(data_dict[ch_id]["resistance"]), np.mean(data_dict[ch_id]["temp_C"])] for ch_id in key_list])
# %%
    # fig, axes = plt.subplots(nrows=len(key_list), sharex = True, sharey = False)
    
    # resample_count = np.min([savgol_dict[ch_id].size for ch_id in savgol_dict.keys()])
    # min_t = np.max([np.min(time_s_dict[ch_id][:10]) for ch_id in time_s_dict.keys()])
    # max_t = np.min([np.max(time_s_dict[ch_id][-10:]) for ch_id in time_s_dict.keys()])
    
    # time_points = np.linspace(min_t, max_t, resample_count)
    # interp_y = np.zeros([len(key_list), resample_count], dtype=float)
    # for i in range(len(key_list)):
    #     ch_id = key_list[i]
    #     x_data = time_s_dict[ch_id]
    #     y_data = savgol_dict[ch_id]
        
    #     new_y = np.interp(time_points, x_data, y_data)
    #     interp_y[i, :] = new_y
    #     axes[i].plot(x_data, y_data, 
    #                  color="k",
    #                  marker=".", ms=5, ls="-", lw=2)
        
    #     axes[i].plot(time_points, new_y, 
    #                  color=COLOR_CYCLE[i%len(COLOR_CYCLE)],
    #                  marker=".", ms=5, ls="-", lw=2, alpha=1)
        
        
        