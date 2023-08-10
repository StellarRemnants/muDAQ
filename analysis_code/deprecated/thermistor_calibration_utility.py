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



calibrate_setup = "joseph"
# calibrate_setup = "kavya"
# calibrate_setup = "solderboard"
orig_fit_level = 3
new_fit_level = orig_fit_level

if calibrate_setup.lower() == "joseph":
    
    # factory_file = "thermistor_factory_calibration_data.csv"
    calibrations_file_path = ("/home/stellarremnants/muDAQ/"
                              "combined_calibration_recirculating_water_bath_2022-07-18.csv")
    
    file_path_prefix = "thermistor_data/joseph_water_bath_calibration/jwbc_"

    sensor_type = "micro_betachip"
    
    pin_ids = [11, 16, 29, 33, 34]
    T_range = [25, 55]
    step_size = 1
    
elif calibrate_setup.lower() == "kavya":
    
    file_path_prefix = "thermistor_data/kavya_water_bath_calibration/kwbc_"
    calibrations_file_path = ("/home/stellarremnants/muDAQ/"
                              "combined_calibration_recirculating_water_bath_2022-07-18.csv")

    sensor_type = "amphenol"
    
    pin_ids = [13, 16, 29, 11, 34, 33, 31]
    T_range = [25, 55]
    step_size = 1
    
elif calibrate_setup.lower() == "solderboard":
    
    file_path_prefix = "thermistor_data/solderboard_prototype_water_bath_calibration/sbwbc_"
    calibrations_file_path = ("/home/stellarremnants/muDAQ/"
                              "controller_code/water_bath_calibrations/"
                              "solderboard_calibrations.csv")

    sensor_type = "amphenol"
    
    pin_ids = [29, 11, 34, 33, 16, 31, 13]
    T_range = [30, 40]
    step_size = 2
    
else:
    raise Exception(f"Unrecognized calibrate_setup key: {calibrate_setup}")

T1_key = "T1"
T2_key = "T2"
TC_key = "TC"
File_num_key = "File#"



pd = pandas.read_csv(calibrations_file_path, 
                     skipinitialspace=True, 
                     dtype={
                         T1_key:float, 
                         T2_key:float, 
                         TC_key:float, 
                         File_num_key:str
                         })
s1 = np.asarray(pd[T1_key])
s2 = np.asarray(pd[T2_key])
cr = np.asarray(pd[TC_key])
file_list = np.asarray(pd[File_num_key], dtype=str)

# factory_data = pandas.read_csv(factory_file)

# def R_of_T_factory(T):
#     return np.interp(T, factory_data["T"], factory_data["R"])

# %%

# s1 = np.zeros([len(file_list)], dtype=float)
# s2 = np.zeros([len(file_list)], dtype=float)
# cr = np.zeros([len(file_list)], dtype=float)

# for i in range(len(file_list)):
#     s1[i] = file_list[i][0]
#     s2[i] = file_list[i][1]
#     cr[i] = file_list[i][2]
    
# %%

# NUM_CHANNELS = 5
error_ids = [f"{pin_ids[i]}_err" for i in range(len(pin_ids))]
column_names = []
for i in range(len(pin_ids)):
    column_names.append(pin_ids[i])
    column_names.append(error_ids[i])
NUM_CHANNELS = len(pin_ids)
NUM_COLUMNS = 2 * NUM_CHANNELS
resistances = pandas.DataFrame(np.zeros([len(file_list), NUM_COLUMNS], dtype=float),
                               columns=column_names)


for i in range(len(file_list)):
    # T1, T2, Tc, file_path_affix = file_list[i]
    file_path_affix = file_list[i]
    file_path = f"{file_path_prefix}{file_path_affix}.csv"
    data_dict, device_dict, start_datetime = process_data_from_path(file_path,
                                                                    correct_on_sensor_id=False)
    
    keys_list = list(data_dict.keys())
    # if len(keys_list) != NUM_CHANNELS:
    #     raise Exception(f"data file: \"{file_path}\" contains the wrong number of channels!")
    for j in range(len(keys_list)):
        
        ch_key = keys_list[j]
        
        if not(ch_key in pin_ids):
            raise Exception(f"ch_id {ch_key} not recognized")
        err_key = f"{ch_key}_err"
        
        resistances.iloc[i].loc[ch_key] = np.mean(data_dict[ch_key]["resistance"])
        std = np.std(data_dict[ch_key]["resistance"])
        # stderr = std / (len(data_dict[ch_key]["resistance"]))**0.5
        resistances.iloc[i].loc[err_key] = std
    
# resistances.drop([29], axis=1, inplace=True)
# pin_ids = [11, 16, 33, 34]
# NUM_CHANNELS = len(pin_ids)
# %%
resistances = resistances.assign(**{T1_key:s1, T2_key:s2, TC_key:cr})
resistances = resistances.sort_values(by=TC_key, ignore_index=True)

# %%
# T_range = [25, 55]
# T_range =[int(np.min(resistances[TC_key])), int(np.max(resistances[TC_key]))]
# T_size = T_range[1] - T_range[0] + 1
offset = 0.5
# counts, edges = np.histogram(resistances[TC_key], bins=T_size, range=T_range)
edges = np.arange(T_range[0], T_range[1]+2*step_size, step=step_size, ) - offset
counts, _ = np.histogram(resistances[TC_key], bins=edges)
columns = []
for col in resistances.columns:
    # col = str(col)
    if type(col) is str:
        if not ("_err" in col):
            columns.append(col)
            columns.append(f"{col}_err")
    else:
        columns.append(col)
        columns.append(f"{col}_err")
        
data_means = pandas.DataFrame(np.zeros([counts.size, len(columns)]),
                              columns=columns)

for i in range(counts.size):
    pd_slice = resistances[np.logical_and(
    resistances[TC_key] >= edges[i],
    resistances[TC_key] < edges[i+1]
    )]
    for col in columns:
        if type(col) is str:
            if not ("_err" in col):
                data_means.iloc[i].loc[col] = np.mean(pd_slice[col])
                data_means.iloc[i].loc[f"{col}_err"] = np.std(pd_slice[col])
                # data_means.iloc[i].loc[f"{col}_err"] = np.mean(pd_slice[f"{col}_err"])
        else:
            data_means.iloc[i].loc[col] = np.mean(pd_slice[col])
            # data_means.iloc[i].loc[f"{col}_err"] = np.std(pd_slice[col])
            data_means.iloc[i].loc[f"{col}_err"] = np.mean(pd_slice[f"{col}_err"])
        
        
# %%
T1_err_key = f"{T1_key}_err"
T2_err_key = f"{T2_key}_err"
TC_err_key = f"{TC_key}_err"

T1 = data_means[T1_key]
T2 = data_means[T2_key]
TM = np.mean([T1, T2], axis=0)
TC = data_means[TC_key]

T1_err = data_means[T1_err_key]
T2_err = data_means[T2_err_key]
TC_err = data_means[TC_err_key]
TM_err = np.std([T1, T2], axis=0)

data_labels = ["T1", "T2", "TM", "TC"]
data_series = [T1, T2, TM, TC]
error_series = [T1_err, T2_err, TM_err, TC_err]

Thermocouple_measurement_uncertainty = 0.05
for error in error_series:
    error[abs(error) < Thermocouple_measurement_uncertainty] = Thermocouple_measurement_uncertainty

min_res_error = 3.69923722e-01
# %%
# R1 = R_of_T_factory(T1)
NROWS = 3

lw = 0.75
marker="."
ms = 5

fig, axes = plt.subplots(nrows=NROWS, ncols=NUM_CHANNELS, sharex='row', sharey='row')
fig.set_size_inches(np.asarray([1920, 1080])/fig.dpi)


for i in range(NUM_CHANNELS):
    upax = axes[0,i]
    midax = axes[1,i]
    downax = axes[2,i]
    
    ch_id = pin_ids[i]
    ch_err_key = f"{ch_id}_err"
    
    upax.set_title(f"Channel: {ch_id}")
    upax.set_xlabel(rf"Channel {ch_id} Resistance [$\Omega$]")
    midax.set_xlabel(rf"Channel {ch_id} Uncorrected T [$^\circ$C]")
    downax.set_xlabel(rf"Channel {ch_id} Uncorrected T [$^\circ$C]")
    
    res = data_means[ch_id]
    res_err = data_means[ch_err_key]
    
    res_err[abs(res_err) < min_res_error] = min_res_error
    
    uncorrected_T_of_res = ln_fit_variable(res, *FIT_DICT[sensor_type][orig_fit_level])
    uncorrected_T_uncertainty = abs(
        ln_fit_variable(
            res-res_err, *FIT_DICT[sensor_type][orig_fit_level]
        ) - \
        ln_fit_variable(
            res+res_err, *FIT_DICT[sensor_type][orig_fit_level]
            )
        )
    
    for j in range(len(data_labels)):
        # pass
        color = COLOR_CYCLE[j%len(COLOR_CYCLE)]
        upax.errorbar(
            res, data_series[j],
            xerr=res_err,
            yerr=error_series[j],
            label=data_labels[j],
            marker=marker,
            color=color,
            ms=ms,
            lw=lw
            )
        
        downax.errorbar(
            uncorrected_T_of_res, data_series[j],
            xerr=uncorrected_T_uncertainty,
            yerr=error_series[j],
            label=data_labels[j],
            marker=marker,
            color=color,
            ms=ms,
            lw=lw
            )
        
        midax.plot(
            uncorrected_T_of_res, data_series[j] - uncorrected_T_of_res,
            label=data_labels[j],
            marker=marker,
            color=color,
            ms=ms,
            lw=lw
            )
    
    downax.plot(uncorrected_T_of_res, uncorrected_T_of_res,
                color="grey",
                label="1:1")
        
    upax.legend(loc="upper right")
    midax.legend(loc="lower left")
    downax.legend(loc="lower right")
    
axes[0,0].set_ylabel(r"T.coupl. T [$^\circ$C]")
axes[1,0].set_ylabel(r"T Misfit [$^\circ$C]")
axes[2,0].set_ylabel(r"T.coupl. T [$^\circ$C]")
[[ax.grid() for ax in row] for row in axes]

fig.suptitle(f"{calibrate_setup.upper()} - UNCORRECTED\nRecirculating Water Bath Calibrations 2022-07-16")

plt.subplots_adjust(
    left=0.05,
    right=0.95,
    top=0.9,
    bottom=0.1,
    hspace=0.3,
    wspace=0.15,
    )

# %%
NROWS = 2

lw = 0.75
marker="."
ms = 5

print_sources = ["TM"]

fig, axes = plt.subplots(nrows=NROWS, ncols=NUM_CHANNELS, sharex=True, sharey='row')
fig.set_size_inches(np.asarray([1920, 1080])/fig.dpi)

channel_names = {}
for pin_id in data_dict.keys():
    matches = []
    for ch_dict in device_dict["channel_list"]:
        if ch_dict['pin_id'] == pin_id:
            matches.append(ch_dict["channel_name"])
            
    if len(matches) < 1:
        print(f"No matches found for channel {pin_id}")
    elif len(matches) > 1:
        print(f"Multiple matches found for channel {pin_id}")
        
    else:
        channel_names[pin_id] = matches[0]


for i in range(NUM_CHANNELS):
    upax = axes[0,i]
    downax = axes[1,i]
    
    print(
        "---\n"
        f"CH: {pin_ids[i]} :: \"{channel_names[pin_ids[i]]}\"\n"
        "---"
        )
    
    ch_id = pin_ids[i]
    ch_err_key = f"{ch_id}_err"
    
    upax.set_title(f"Channel: {ch_id}")
    downax.set_xlabel(rf"Channel {ch_id} Orig. T [$^\circ$C]")
    
    res = data_means[ch_id]
    res_err = data_means[ch_err_key]
    
    res_err[abs(res_err) < min_res_error] = min_res_error
    
    uncorrected_T_of_res = ln_fit_variable(res, *FIT_DICT[sensor_type][orig_fit_level])
    uncorrected_T_uncertainty = abs(
        ln_fit_variable(
            res-res_err, *FIT_DICT[sensor_type][orig_fit_level]
        ) - \
        ln_fit_variable(
            res+res_err, *FIT_DICT[sensor_type][orig_fit_level]
            )
        )
    
    for j in range(len(data_labels)):
        # pass
        color = COLOR_CYCLE[j%len(COLOR_CYCLE)]
        
        uncorrected_misfit = data_series[j]-uncorrected_T_of_res
        cond = np.isfinite(res)
        fit_res = res[cond]
        fit_T = data_series[j][cond]
        fit_params, covar = polynomial_fit(fit_res, fit_T, max_pow=new_fit_level)
        corrected_data = polynomial_variable(res, *fit_params)
        corrected_misfit = data_series[j]-corrected_data
        err_max = np.max(abs(corrected_misfit))
        
        if data_labels[j] in print_sources:
            print(f"Source: {data_labels[j]}")
            print(f"Fit:\n[",end="")
            for fit in fit_params:
                print(f"{fit:.7e}, ", end="")
            print("]")
            print(f"Max Misfit: {err_max}")
            print()
        
        upax.plot(
            uncorrected_T_of_res, uncorrected_misfit,
            label=f"{data_labels[j]}",
            color=color,
            marker=marker,
            ms=ms,
            lw=lw
            )
        
        downax.plot(
            uncorrected_T_of_res, corrected_misfit,
            label=f"{data_labels[j]}",
            marker=marker,
            color=color,
            ms=ms,
            lw=lw,
            ls="--"
            )
        
    upax.legend(loc="lower left")
    downax.legend(loc="lower left")
    
axes[0,0].set_ylabel(r"Uncorrected T Misfit [$^\circ$C]")
axes[1,0].set_ylabel(r"Corrected T Misfit [$^\circ$C]")
[[ax.grid() for ax in row] for row in axes]
# [ax.grid() for ax in axes]

fig.suptitle(f"{calibrate_setup.upper()} - CORRECTION MISFIT\nRecirculating Water Bath Calibrations 2022-07-16")

plt.subplots_adjust(
    left=0.05,
    right=0.95,
    top=0.9,
    bottom=0.1,
    hspace=0.0,
    wspace=0.15,
    )
    
        
# %%
# NROWS = 2
# fig, axes = plt.subplots(ncols=NUM_CHANNELS, nrows=NROWS, sharex='row', sharey='row')
# fig.set_size_inches(np.asarray([1920, 1080])/fig.dpi)
# twinaxes = np.asarray([np.asarray([ax.twinx() for ax in axes[i, :]]) for i in range(NROWS)])
# twinaxes[0,0].get_shared_y_axes().join(*twinaxes[0,:])
# twinaxes[1,0].get_shared_y_axes().join(*twinaxes[1,:])
# fit_level = 6
# max_correct_pow = 6
# sensor_types = ["micro_betachip"] * NUM_CHANNELS

# # color_cycle = ["red", "green", "blue"]
# color_cycle=COLOR_CYCLE

# rs_of_t_labels = ["S1", "S2", "Ctr"]
# DARKENING = 0.35

# # t_vals = [s1, s2, cr]
# t_vals = [s1]
# rs_of_t = [R_of_T_factory(s) for s in t_vals]
# for i in range(NUM_CHANNELS):
    
#     print(
#         "---\n"
#         f"CH: {pin_ids[i]}\n"
#         "---"
#         )
#     ax = axes[0, i]
#     twinax = twinaxes[0, i]
#     ax2 = axes[1, i]
#     twinax2 = twinaxes[1, i]
#     ax.grid()
#     ax2.grid()
    
#     if i < NUM_CHANNELS - 1:
#         twinax.axes.get_yaxis().set_visible(False)
#         twinax2.axes.get_yaxis().set_visible(False)
    
#     r_meas = np.asarray(resistances[pin_ids[i]])
    
#     sensor_type = sensor_types[i]
#     T_meas = ln_fit_variable(r_meas, *FIT_DICT[sensor_type][fit_level])
    
#     ax2.plot(T_meas, T_meas, color="grey")

#     ax.plot(r_meas, r_meas, color="grey")
#     ax.set_title(f"Channel {pin_ids[i]}")
#     ax.set_xlabel(rf"CH {pin_ids[i]} Resistance [$\Omega$]")
#     ax2.set_xlabel(rf"CH {pin_ids[i]} Temperature [$^\circ$C]")
    
#     for j in range(len(rs_of_t)):
#         r_of_t = rs_of_t[j]
#         fit_params, covar = polynomial_fit(r_meas, r_of_t, max_pow=max_correct_pow)
        
#         print(f"Source: {rs_of_t_labels[j]}")
#         print(f"Fit:\n{fit_params}")
        
#         new_r = polynomial_variable(r_meas, *fit_params)
#         diff = r_of_t - r_meas
#         new_diff = r_of_t - new_r
        
#         color = color_cycle[j%len(color_cycle)]
#         dark_color = darken_color(color, proportion=DARKENING)
        
#         ax.plot(r_meas, r_of_t, color=dark_color, marker=".")
#         ax.plot(r_meas, new_r, color=color, marker=".")
#         twinax.plot(r_meas, diff, ls="--", color=dark_color, marker=".")
#         twinax.plot(r_meas, new_diff, ls="--", color=color, marker=".")
        
        
#         new_T = ln_fit_variable(new_r, *FIT_DICT[sensor_type][fit_level])
#         ax2.plot(T_meas, t_vals[j], color=dark_color)
#         ax2.plot(new_T, t_vals[j], color=color)
        
#         old_T_diff = t_vals[j] - T_meas
#         new_T_diff = t_vals[j] - new_T
        
#         twinax2.plot(T_meas, old_T_diff, color=dark_color, ls="--", marker=".")
#         twinax2.plot(T_meas, new_T_diff, color=color, marker=".", ls="--")
        
#         max_diff = np.max(abs(new_T_diff))
#         print(f"Max Diff: {max_diff}")
        
#         # ax.set_edgecolor("k")
#         print()

# axes[0,0].set_ylabel(r'Thermocouple "Resistance" [$\Omega$]')
# axes[1,0].set_ylabel(r"Thermocouple Temperature [$^\circ$C]")
# twinaxes[0,-1].set_ylabel(r"Resistance Misfit [$\Omega$]")
# twinaxes[1,-1].set_ylabel(r"Temperature Misfit [$^\circ$C]")
# plt.subplots_adjust(
#     left=0.05,
#     right=0.95,
#     top=0.9,
#     bottom=0.1,
#     hspace=0.2,
#     wspace=0.05,
#     )
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