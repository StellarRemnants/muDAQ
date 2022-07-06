#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 16:05:50 2022

@author: stellarremnants
"""

import numpy as np
import pandas
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def ln_fit_variable(R, *args):
    log_R = np.log(R)
    dat = np.zeros_like(log_R)
    
    for i in range(len(args)):
        dat += args[i] * log_R ** i
    return dat

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

factory_file = "amphenol_calibration_data.csv"
factory_data = pandas.read_csv(factory_file)

resistance_key = "resistance"
temp_C_key = "temp_C"

powers = np.arange(0, 10)

fits = {}
init=1
for p in powers:
    params, covar = curve_fit(ln_fit_variable, 
                              factory_data[resistance_key],
                              factory_data[temp_C_key], 
                              p0=[init]*(p+1))
    
    fits[p] = params
    
# %%
fig, axes = plt.subplots(nrows=2, sharex=True)
# twinx = ax.twinx()

axes[0].semilogx(factory_data[resistance_key], factory_data[temp_C_key],
        color="k", marker=".",)

for i in range(len(powers)):
    p = powers[i]
    color=COLOR_CYCLE[i%len(COLOR_CYCLE)]
    y = ln_fit_variable(factory_data[resistance_key], *fits[p])
    axes[0].semilogx(
        factory_data[resistance_key],
        y,
        color=color,
        marker=".",
        ls="-",
        label=f"pow={p}"
        )
    misfit = abs(factory_data[temp_C_key] - y)
    axes[1].loglog(
        factory_data[resistance_key],
        misfit,
        color=color,
        marker=".",
        ls="-",
        label=f"pow={p}"
        )
    
    max_misfit = np.max(misfit)
    print(f"{p} : {max_misfit}")
    
axes[0].legend(loc="upper right")
axes[1].legend(loc="upper right")

axes[0].grid(which="both")
axes[1].grid(which="both")

# def R_of_T_factory(T):
#     return np.interp(T, factory_data["T"], factory_data["R"])

