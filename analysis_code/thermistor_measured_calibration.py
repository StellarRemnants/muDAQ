#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 20:13:48 2022

@author: stellarremnants
"""

import numpy as np
import pandas
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

from file_read_functions import thermistor_temp_C_from_resistance
# from thermistor_calibration import ln_fit_fnc, ln_fit_variable

factory_file = "thermistor_factory_calibration_data.csv"
data_file = "Thermistor Calibration 2.csv"

dataframe = pandas.read_csv(data_file)
factory_data = pandas.read_csv(factory_file)


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


def R_of_T_factory(T):
    return np.interp(T, factory_data["T"], factory_data["R"])


def linear(x, a, b):
    return a*x + b

def ln(x, a, b, c):
    return a*np.log(b*x)+c

def exp(x, a, b, c):
    return a*np.exp(b*x)+c
# %%
R_Meas = R_of_T_factory(dataframe["MEAS"])
R_11 = dataframe["R11"]
R_29 = dataframe["R29"]

fig, axes = plt.subplots(ncols=2, sharex=False, sharey=False)
fig.set_size_inches(np.asarray([1920,1080])/fig.dpi)
twin_axes = [axes[i].twinx() for i in range(len(axes))]

axes[0].set_ylabel(r"R(T_Measured) [$\Omega$]")
axes[0].set_xlabel(r"R_Measured CH 11 [$\Omega$]")
axes[1].set_xlabel(r"R_Measured CH 29 [$\Omega$]")
axes[0].set_aspect("equal")
axes[1].set_aspect("equal")
axes[0].grid("both")
axes[1].grid("both")
kwargs = {
    "marker":".",
    "ms":5,
    "color":COLOR_CYCLE[0]
    }
axes[0].plot(R_11, R_Meas, **kwargs)
axes[1].plot(R_29, R_Meas, **kwargs)

linfits_11, linerrors_11 = curve_fit(linear, R_11, R_Meas)
linfits_29, linerrors_29 = curve_fit(linear, R_29, R_Meas)

kwargs["color"] = COLOR_CYCLE[1]
y_data_11 = linear(R_11, *linfits_11)
y_data_29 = linear(R_29, *linfits_29)
axes[0].plot(R_11, y_data_11, **kwargs)
axes[1].plot(R_29, y_data_29, **kwargs)

kwargs["color"] = COLOR_CYCLE[2]
twin_axes[0].plot(R_11, R_Meas-y_data_11, **kwargs)
twin_axes[1].plot(R_11, R_Meas-y_data_29, **kwargs)

kwargs["color"] = "k"
twin_axes[0].plot(R_11, (R_Meas-np.mean(R_Meas)) - (R_11-np.mean(R_11)), **kwargs)
twin_axes[1].plot(R_29, (R_Meas-np.mean(R_Meas)) - (R_29-np.mean(R_29)), **kwargs)


# kwargs["color"] = COLOR_CYCLE[2]
# axes[0].plot(R_11, (R_11*linfits_11[0]) + linfits_11[1], **kwargs)
# axes[1].plot(R_29, (R_29*linfits_29[0]) + linfits_29[1], **kwargs)

# kwargs["color"] = "k"
# axes[0].plot(R_11, R_11, **kwargs)
# axes[1].plot(R_29, R_29, **kwargs)


# logfits_11, logerrors_11 = curve_fit(ln, R_11, R_Meas, 
#                          bounds=([-np.inf, 0, -np.inf], [np.inf, np.inf, np.inf]))
# logfits_29, logerrors_29 = curve_fit(ln, R_29, R_Meas, 
#                          bounds=([-np.inf, 0, -np.inf], [np.inf, np.inf, np.inf]))
# kwargs["color"] = COLOR_CYCLE[2]
# axes[0].plot(ln(R_11, *logfits_11), R_Meas, **kwargs)
# axes[1].plot(ln(R_29, *logfits_29), R_Meas, **kwargs)


# expfits_11, experrors_11 = curve_fit(exp, R_11, R_Meas, p0=[1,0,0])
# expfits_29, experrors_29 = curve_fit(exp, R_11, R_Meas, p0=[1,0,0])
# kwargs["color"] = COLOR_CYCLE[3]
# axes[0].plot(ln(R_11, *expfits_11), R_Meas, **kwargs)
# axes[1].plot(ln(R_29, *expfits_29), R_Meas, **kwargs)


# %%%

def polynomial_variable(x, *args):
    ret = np.zeros_like(x)
    for i in range(len(args)):
        ret += args[i] * x**i
    return ret

def polynomial_fit(xdata, ydata, max_pow = None, p0=None):
    if max_pow is None and p0 is None:
        return ValueError("Must specify one of max_pow or p0")
    elif p0 is None:
        p0 = [1] * (max_pow+1)
    
    return curve_fit(polynomial_variable, xdata, ydata, p0=p0)
    
fig, axes = plt.subplots(ncols=2, sharey=False)
fig.set_size_inches(np.asarray([1920,1080])/fig.dpi)
max_pow = 4
twin_axes = [axes[i].twinx() for i in range(len(axes))]
axes[0].set_ylabel(r"R(T_Measured) [$\Omega$]")
axes[0].set_xlabel(r"R_Measured CH 11 [$\Omega$]")
axes[1].set_xlabel(r"R_Measured CH 29 [$\Omega$]")
axes[0].set_aspect("equal")
axes[1].set_aspect("equal")
axes[0].grid("both")
axes[1].grid("both")

polyfits_11, errors = polynomial_fit(R_11, R_Meas, max_pow=max_pow)
y_fit_11 = polynomial_variable(R_11, *polyfits_11)
kwargs["color"] = COLOR_CYCLE[0]
axes[0].plot(R_11, R_Meas, **kwargs)
kwargs["color"] = COLOR_CYCLE[1]
axes[0].plot(R_11, y_fit_11, **kwargs)
kwargs["color"] = COLOR_CYCLE[2]
twin_axes[0].plot(R_11, R_Meas - y_fit_11, **kwargs)
print(polyfits_11)

polyfits_29, errors = polynomial_fit(R_29, R_Meas, max_pow=max_pow)
y_fit_29 = polynomial_variable(R_29, *polyfits_29)
kwargs["color"] = COLOR_CYCLE[0]
axes[1].plot(R_29, R_Meas, **kwargs)
kwargs["color"] = COLOR_CYCLE[1]
axes[1].plot(R_29, y_fit_29, **kwargs)
kwargs["color"] = COLOR_CYCLE[2]
twin_axes[1].plot(R_29, R_Meas - y_fit_29, **kwargs)
print(polyfits_29)


kwargs["color"] = "k"
twin_axes[0].plot(R_11, (R_Meas-np.mean(R_Meas)) - (R_11-np.mean(R_11)), **kwargs)
twin_axes[1].plot(R_29, (R_Meas-np.mean(R_Meas)) - (R_29-np.mean(R_29)), **kwargs)

dtwin_axes = [twin_axes[i] for i in range(len(twin_axes))]
kwargs["color"] = "red"

temp_misfit_11 = thermistor_temp_C_from_resistance(R_Meas)\
    -thermistor_temp_C_from_resistance(y_fit_11)
dtwin_axes[0].plot(R_11, temp_misfit_11, **kwargs)
temp_misfit_29 = thermistor_temp_C_from_resistance(R_Meas)\
    -thermistor_temp_C_from_resistance(y_fit_29)
dtwin_axes[1].plot(R_29, temp_misfit_29, **kwargs)

print(np.max(abs(temp_misfit_11)))
print(np.max(abs(temp_misfit_29)))

# %%
# def fnc(x, *args):
#     ret = np.zeros_like(x)
#     for i in range(len(args)):
#         ret += args[i] * x**i
#     return ret
# x = np.linspace(0, 10, 100)
# p0 = [4, 3, 2, 1]
# y = fnc(x, *p0)

# fig, ax = plt.subplots()
# ax.plot(x, y)


