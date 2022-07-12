#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 12:22:36 2022

@author: stellarremnants
"""

import numpy as np
import pandas
import matplotlib.pyplot as plt
import os

from scipy.optimize import curve_fit
from file_read_functions import (
    process_data_from_path,
    thermistor_temp_C_from_resistance
    )

calibration_notes = [

[25.9, 26.0, 30.3, "00-04_02_calibration_0000.csv"],
[26.1, 26.2, 30.7, "00-04_02_calibration_0001.csv"],
[26.6, 26.7, 33.6, "00-04_02_calibration_0002.csv"],
[27.3, 27.4, 33.0, "00-04_02_calibration_0003.csv"],
[27.9, 28.0, 34.0, "00-04_02_calibration_0004.csv"],
[28.3, 28.4, 35.0, "00-04_02_calibration_0005.csv"],
[29.0, 29.0, 36.2, "00-04_02_calibration_0006.csv"],
[29.5, 29.6, 37.1, "00-04_02_calibration_0007.csv"],
[30.0, 30.2, 38.1, "00-04_02_calibration_0008.csv"],
[30.4, 30.6, 39.1, "00-04_02_calibration_0009.csv"],
[31.0, 31.0, 40.0, "00-04_02_calibration_0010.csv"],
[31.3, 31.4, 41.1, "00-04_02_calibration_0011.csv"],
[33.6, 33.5, 42.1, "00-04_02_calibration_0012.csv"],
[34.2, 34.2, 43.0, '00-04_02_calibration_0013.csv'],
[34.4, 34.4, 43.9, "00-04_02_calibration_0014.csv"],
[34.5, 34.5, 44.0, '00-04_02_calibration_0015.csv'],
[34.8, 34.7, 45.0, '00-04_02_calibration_0016.csv'],
[35.0, 35.0, 46.1, "00-04_02_calibration_0017.csv"],
[35.4, 35.4, 46.9, "00-04_02_calibration_0018.csv"],
[35.7, 35.7, 48.0, "00-04_02_calibration_0019.csv"],
[35.9, 35.9, 48.9, "00-04_02_calibration_0020.csv"],
[36.3, 36.3, 49.9, "00-04_02_calibration_0021.csv"],
[36.6, 36.6, 51.0, "00-04_02_calibration_0022.csv"],
[37.0, 37.0, 51.9, "00-04_02_calibration_0023.csv"],
[37.3, 37.3, 53.0, '00-04_02_calibration_0024.csv'],
[37.8, 37.7, 54.0, "00-04_02_calibration_0025.csv"],
[38.2, 38.1, 55.0, "00-04_02_calibration_0026.csv"],

]

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

PROP_CYCLE = plt.rcParams['axes.prop_cycle']
COLOR_CYCLE = PROP_CYCLE.by_key()['color']

data_file_dir = "thermistor_data"

CH_IDS = [11, 16, 29, 33, 34]
NUM_CHANNELS = len(CH_IDS)
NUM_DATAPOINTS = len(calibration_notes)

columns = [*CH_IDS, "T1", "T2", "Tctr"]
resistance_dataframe = pandas.DataFrame(
    np.zeros([NUM_DATAPOINTS, len(columns)]),
    columns=columns
    )

factory_data = "micro_betachip_factory_calibration.csv"
factory_dataframe = pandas.read_csv(factory_data)
def R_of_T_factory(T_in):
    return np.interp(T_in, 
                     factory_dataframe["temp_C"], 
                     factory_dataframe["resistance"]
                     )

for i in range(len(calibration_notes)):
    
    T1, T2, Tctr, file_name = calibration_notes[i]
    
    file_path = os.path.join(data_file_dir, file_name)
    
    # print(file_path)
    # print(os.path.exists(file_path))
    
    data_dict, device_dict, start_datetime = process_data_from_path(
        file_path,
        correct_on_sensor_id=False
        )
    
    resistance_dataframe.iloc[i].loc["T1"] = T1
    resistance_dataframe.iloc[i].loc["T2"] = T2
    resistance_dataframe.iloc[i].loc["Tctr"] = Tctr
    
    for ch_id in data_dict.keys():
        temp_resistance = np.mean(data_dict[ch_id]["resistance"])
        resistance_dataframe.iloc[i].loc[ch_id] = temp_resistance
        
def polynomial_function(x, *args):
    y = np.zeros_like(x)
    for i in range(len(args)):
        y += args[i] * x**i
    return y


fig, axes = plt.subplots(ncols=NUM_CHANNELS, nrows=2, 
                         sharex='col',
                         sharey='row',)
T_fig, T_axes = plt.subplots(ncols=NUM_CHANNELS, nrows=2,
                         sharex='col',
                         sharey='row',)

# R1 = R_of_T_factory(resistance_dataframe["T1"])
# R2 = R_of_T_factory(resistance_dataframe["T2"])
# Rctr = R_of_T_factory(resistance_dataframe["Tctr"])

MAX_POW = 6
p0 = [1]*(MAX_POW+1)

S_labels = ["T1", "T2", "Tctr"]
T_series = [resistance_dataframe[s] for s in S_labels]
R_series = [R_of_T_factory(T) for T in T_series]

print("FIT PARAMS")
for i in range(NUM_CHANNELS):
    ch_id = CH_IDS[i]
    print("----")
    print(f"CH: {CH_IDS[i]}")
    print("----")
    ch_resistance = resistance_dataframe[ch_id]
    
    for j in range(len(T_series)):
        print(f"Sensor: {S_labels[j]}")
        color = COLOR_CYCLE[j%len(COLOR_CYCLE)]
        dark_color = darken_color(color)
        
        fit_params, _ = curve_fit(polynomial_function, 
                                  ch_resistance,
                                  R_series[j],
                                  p0=p0
                                  )
        print(fit_params)
        print()
        new_R = polynomial_function(ch_resistance, *fit_params)
        
        axes[0,i].plot(ch_resistance, R_series[j],
                       color=dark_color,
                       marker = ".",
                       ms=10
                       )
        axes[0,i].plot(ch_resistance, new_R,
                       color=color,
                       marker = ".",
                       ms=10)
    
        axes[1,i].plot(ch_resistance, R_series[j]-new_R,
                       color=color,
                       marker = ".",
                       ms=10)
        
        
        ch_T = thermistor_temp_C_from_resistance(
            ch_resistance,
            thermistor_type="micro_betachip"
            )
        new_T = thermistor_temp_C_from_resistance(
            new_R,
            thermistor_type="micro_betachip"
            )
        
        T_axes[0,i].plot(ch_T, T_series[j],
                       color=dark_color,
                       marker = ".",
                       ms=10)
        T_axes[0,i].plot(ch_T, new_T,
                       color=color,
                       marker = ".",
                       ms=10)
        
        T_axes[1,i].plot(ch_T, T_series[j]-new_T,
                       color=color,
                       marker = ".",
                       ms=10)
    
    
    axes[1,i].set_xlabel(rf"CH:{CH_IDS[i]} Resistance [$\Omega$]")
    T_axes[1,i].set_xlabel(rf"CH:{CH_IDS[i]} Temperature [$^\circ$C]")
    
    axes[0,i].set_title(f"Channel {CH_IDS[i]}")
    T_axes[0,i].set_title(f"Channel {CH_IDS[i]}")
    
    axes[0,i].grid()
    axes[1,i].grid()
    T_axes[0,i].grid()
    T_axes[1,i].grid()
    
    
    
axes[0,0].set_ylabel(r"Thermocouple 'Resistance' [$\Omega$]")
axes[1,0].set_ylabel(r"Calibration Misfit [$\Omega$]")


T_axes[0,0].set_ylabel(r"Thermocouple Temperature [$^\circ$C]")
T_axes[1,0].set_ylabel(r"Calibration Misfit [$^\circ$C]")

fig.suptitle("Thermistor Calibration: Resistance")
T_fig.suptitle("Thermistor Calibration: Temperature")
fig.set_size_inches(np.asarray([1920, 1080])/fig.dpi)
T_fig.set_size_inches(np.asarray([1920, 1080])/fig.dpi)