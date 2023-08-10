#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 17:51:59 2022

@author: stellarremnants
"""

import numpy as np
import pandas
import matplotlib.pyplot as plt
from file_read_functions import (
    process_data_from_path,
    ln_fit_variable,
    FIT_DICT,
    )
from thermistor_calibration_library import (
    polynomial_fit,
    polynomial_variable
    )


PROP_CYCLE = plt.rcParams['axes.prop_cycle']
COLOR_CYCLE = PROP_CYCLE.by_key()['color']

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

file_prefix = "00-04_02_calibration_"
file_dir = "thermistor_data/"
file_path_prefix = f"{file_dir}{file_prefix}"
file_list = [
    [25.9, 26.0, 30.3, "0000"],
    [26.1, 26.2, 30.7, "0001"],
    [26.6, 26.7, 33.6, "0002"],
    [27.3, 27.4, 33.0, "0003"],
    [27.9, 28.0, 34.0, "0004"],
    [28.3, 28.4, 35.0, "0005"],
    [29.0, 29.0, 36.2, "0006"],
    [29.5, 29.6, 37.1, "0007"],
    [30.0, 30.2, 38.1, "0008"],
    [30.4, 30.6, 39.1, "0009"],
    [31.0, 31.0, 40.0, "0010"],
    [31.3, 31.4, 41.1, "0011"],
    [33.6, 33.5, 42.1, "0012"],
    [34.2, 34.2, 43.0, "0013"],
    [34.4, 34.4, 43.9, "0014"],
    [34.5, 34.5, 44.0, "0015"],
    [34.8, 34.7, 45.0, "0016"],
    [35.0, 35.0, 46.1, "0017"],
    [35.4, 35.4, 46.9, "0018"],
    [35.7, 35.7, 48.0, "0019"],
    [35.9, 35.9, 48.9, "0020"],
    [36.3, 36.3, 49.9, "0021"],
    [36.6, 36.6, 51.0, "0022"],
    [37.0, 37.0, 51.9, "0023"],
    [37.3, 37.3, 53.0, "0024"],
    [37.8, 37.7, 54.0, "0025"],
    [38.2, 38.1, 55.0, "0026"],
    # [29.5, 29.9, 29.7, "thermistor_data/00-04_calibration_0001.csv"],
    # [34.4, 35.5, 35.6, "thermistor_data/00-04_calibration_0002.csv"],
    # [38.3, 39.6, 40.3, "thermistor_data/00-04_calibration_0003.csv"],
    # [42.0, 43.7, 45.5, "thermistor_data/00-04_calibration_0004.csv"],
    # [46.2, 47.6, 50.8, "thermistor_data/00-04_calibration_0005.csv"],
    # [51.3, 65.6, 55.0, "thermistor_data/00-04_calibration_0006.csv"],
    # [52.9, 72.1, 60.8, "thermistor_data/00-04_calibration_0007.csv"],
    # [56.1, 77.7, 65.8, "thermistor_data/00-04_calibration_0008.csv"],
    ]


factory_file = "thermistor_factory_calibration_data.csv"
factory_data = pandas.read_csv(factory_file)

def R_of_T_factory(T):
    return np.interp(T, factory_data["T"], factory_data["R"])

# %%

s1 = np.zeros([len(file_list)], dtype=float)
s2 = np.zeros([len(file_list)], dtype=float)
cr = np.zeros([len(file_list)], dtype=float)

for i in range(len(file_list)):
    s1[i] = file_list[i][0]
    s2[i] = file_list[i][1]
    cr[i] = file_list[i][2]
    
# %%

# NUM_CHANNELS = 5
pin_ids = [11, 16, 29, 33, 34]
NUM_CHANNELS = len(pin_ids)
resistances = pandas.DataFrame(np.zeros([len(file_list), NUM_CHANNELS], dtype=float),
                               columns=pin_ids)


for i in range(len(file_list)):
    T1, T2, Tc, file_path_affix = file_list[i]
    file_path = f"{file_path_prefix}{file_path_affix}.csv"
    data_dict, device_dict, start_datetime = process_data_from_path(file_path,
                                                                    correct_on_sensor_id=False)
    
    keys_list = list(data_dict.keys())
    if len(keys_list) != NUM_CHANNELS:
        raise Exception(f"data file: \"{file_path}\" contains the wrong number of channels!")
    for j in range(len(keys_list)):
        resistances.iloc[i].loc[keys_list[j]] = np.mean(data_dict[keys_list[j]]["resistance"])
        
    
# resistances.drop([29], axis=1, inplace=True)
# pin_ids = [11, 16, 33, 34]
# NUM_CHANNELS = len(pin_ids)
        
# %%
NROWS = 2
fig, axes = plt.subplots(ncols=NUM_CHANNELS, nrows=NROWS, sharex='row', sharey='row')
fig.set_size_inches(np.asarray([1920, 1080])/fig.dpi)
twinaxes = np.asarray([np.asarray([ax.twinx() for ax in axes[i, :]]) for i in range(NROWS)])
twinaxes[0,0].get_shared_y_axes().join(*twinaxes[0,:])
twinaxes[1,0].get_shared_y_axes().join(*twinaxes[1,:])
fit_level = 6
max_correct_pow = 6
sensor_types = ["micro_betachip"] * NUM_CHANNELS

# color_cycle = ["red", "green", "blue"]
color_cycle=COLOR_CYCLE

rs_of_t_labels = ["S1", "S2", "Ctr"]
DARKENING = 0.35

# t_vals = [s1, s2, cr]
t_vals = [s1]
rs_of_t = [R_of_T_factory(s) for s in t_vals]
for i in range(NUM_CHANNELS):
    
    print(
        "---\n"
        f"CH: {pin_ids[i]}\n"
        "---"
        )
    ax = axes[0, i]
    twinax = twinaxes[0, i]
    ax2 = axes[1, i]
    twinax2 = twinaxes[1, i]
    ax.grid()
    ax2.grid()
    
    if i < NUM_CHANNELS - 1:
        twinax.axes.get_yaxis().set_visible(False)
        twinax2.axes.get_yaxis().set_visible(False)
    
    r_meas = np.asarray(resistances[pin_ids[i]])
    
    sensor_type = sensor_types[i]
    T_meas = ln_fit_variable(r_meas, *FIT_DICT[sensor_type][fit_level])
    
    ax2.plot(T_meas, T_meas, color="grey")

    ax.plot(r_meas, r_meas, color="grey")
    ax.set_title(f"Channel {pin_ids[i]}")
    ax.set_xlabel(rf"CH {pin_ids[i]} Resistance [$\Omega$]")
    ax2.set_xlabel(rf"CH {pin_ids[i]} Temperature [$^\circ$C]")
    
    for j in range(len(rs_of_t)):
        r_of_t = rs_of_t[j]
        fit_params, covar = polynomial_fit(r_meas, r_of_t, max_pow=max_correct_pow)
        
        print(f"Source: {rs_of_t_labels[j]}")
        print(f"Fit:\n{fit_params}")
        
        new_r = polynomial_variable(r_meas, *fit_params)
        diff = r_of_t - r_meas
        new_diff = r_of_t - new_r
        
        color = color_cycle[j%len(color_cycle)]
        dark_color = darken_color(color, proportion=DARKENING)
        
        ax.plot(r_meas, r_of_t, color=dark_color, marker=".")
        ax.plot(r_meas, new_r, color=color, marker=".")
        twinax.plot(r_meas, diff, ls="--", color=dark_color, marker=".")
        twinax.plot(r_meas, new_diff, ls="--", color=color, marker=".")
        
        
        new_T = ln_fit_variable(new_r, *FIT_DICT[sensor_type][fit_level])
        ax2.plot(T_meas, t_vals[j], color=dark_color)
        ax2.plot(new_T, t_vals[j], color=color)
        
        old_T_diff = t_vals[j] - T_meas
        new_T_diff = t_vals[j] - new_T
        
        twinax2.plot(T_meas, old_T_diff, color=dark_color, ls="--", marker=".")
        twinax2.plot(T_meas, new_T_diff, color=color, marker=".", ls="--")
        
        max_diff = np.max(abs(new_T_diff))
        print(f"Max Diff: {max_diff}")
        
        # ax.set_edgecolor("k")
        print()

axes[0,0].set_ylabel(r'Thermocouple "Resistance" [$\Omega$]')
axes[1,0].set_ylabel(r"Thermocouple Temperature [$^\circ$C]")
twinaxes[0,-1].set_ylabel(r"Resistance Misfit [$\Omega$]")
twinaxes[1,-1].set_ylabel(r"Temperature Misfit [$^\circ$C]")
plt.subplots_adjust(
    left=0.05,
    right=0.95,
    top=0.9,
    bottom=0.1,
    hspace=0.2,
    wspace=0.05,
    )
# fig.supxlabel("Thermistor Reading")
# fig.supylabel("Thermocouple Reading", 
#               x=0.01,
#               horizontalalignment="center",
#               verticalalignment="center")
# fig.supylabel("Difference", 
#               x=0.95,
#               horizontalalignment="center",
#               verticalalignment="center")
# fig.tight_layout()