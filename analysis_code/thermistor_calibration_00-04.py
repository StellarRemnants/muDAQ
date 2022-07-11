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


file_list = [
    
    [29.5, 29.9, 29.7, "thermistor_data/00-04_calibration_0001.csv"],
    [34.4, 35.5, 35.6, "thermistor_data/00-04_calibration_0002.csv"],
    [38.3, 39.6, 40.3, "thermistor_data/00-04_calibration_0003.csv"],
    [42.0, 43.7, 45.5, "thermistor_data/00-04_calibration_0004.csv"],
    [46.2, 47.6, 50.8, "thermistor_data/00-04_calibration_0005.csv"],
    [51.3, 65.6, 55.0, "thermistor_data/00-04_calibration_0006.csv"],
    [52.9, 72.1, 60.8, "thermistor_data/00-04_calibration_0007.csv"],
    [56.1, 77.7, 65.8, "thermistor_data/00-04_calibration_0008.csv"],
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
    T1, T2, Tc, file_path = file_list[i]
    
    data_dict, device_dict, start_datetime = process_data_from_path(file_path,
                                                                    correct_on_sensor_id=False)
    
    keys_list = list(data_dict.keys())
    if len(keys_list) != NUM_CHANNELS:
        raise Exception(f"data file: \"{file_path}\" contains the wrong number of channels!")
    for j in range(len(keys_list)):
        resistances.iloc[i].loc[keys_list[j]] = np.mean(data_dict[keys_list[j]]["resistance"])
        
# %%
NROWS = 2
fig, axes = plt.subplots(ncols=NUM_CHANNELS, nrows=NROWS, sharex=False, sharey=False)
fig.set_size_inches(np.asarray([1920, 1080])/fig.dpi)
twinaxes = np.asarray([np.asarray([ax.twinx() for ax in axes[i, :]]) for i in range(NROWS)])

fit_level = 6
max_correct_pow = 6
sensor_types = ["micro_betachip"] * NUM_CHANNELS

color_cycle = ["red", "green", "blue"]

# t_vals = (s1, s2, cr)
t_vals = [s1]
rs_of_t = [R_of_T_factory(s) for s in t_vals]
for i in range(NUM_CHANNELS):
    ax = axes[0, i]
    twinax = twinaxes[0, i]
    ax2 = axes[1, i]
    twinax2 = twinaxes[1, i]
    
    r_meas = np.asarray(resistances[pin_ids[i]])
    
    ax.plot(r_meas, r_meas, color="grey")
    ax.set_title(f"Channel {pin_ids[i]}")
    
    for j in range(len(rs_of_t)):
        r_of_t = rs_of_t[j]
        # ax.plot(r_of_t, r_of_t, color="purple")
        
        fit_params, covar = polynomial_fit(r_meas, r_of_t, max_pow=max_correct_pow)
        
        new_r = polynomial_variable(r_meas, *fit_params)
        
        diff = r_of_t - r_meas
        new_diff = r_of_t - new_r
        
        ax.plot(r_meas, r_of_t, color="k", marker=".")
        ax.plot(r_meas, new_r, color=color_cycle[j], marker=".")
        twinax.plot(r_meas, diff, ls="--", color="k", marker=".")
        twinax.plot(r_meas, new_diff, ls="--", color=color_cycle[j], marker=".")
        
        
        
        # fit_vals = [0, 1]
        sensor_type = sensor_types[i]
        T_meas = ln_fit_variable(r_meas, *FIT_DICT[sensor_type][fit_level])
        new_T = ln_fit_variable(new_r, *FIT_DICT[sensor_type][fit_level])
        ax2.plot(T_meas, t_vals[j], color="k")
        ax2.plot(new_T, t_vals[j], color=color_cycle[j])
        
        old_T_diff = t_vals[j] - T_meas
        new_T_diff = t_vals[j] - new_T
        
        twinax2.plot(T_meas, old_T_diff, color="k", ls="--", marker=".")
        twinax2.plot(T_meas, new_T_diff, color=color_cycle[j], marker=".")
        

fig.tight_layout()