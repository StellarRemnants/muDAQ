#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 13:04:07 2022

@author: stellarremnants
"""

import numpy as np
import pandas
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

from file_read_functions import (
    process_data_from_path,
    thermistor_temp_C_from_resistance,
    )

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


factory_file = "thermistor_factory_calibration_data.csv"
factory_data = pandas.read_csv(factory_file)

def R_of_T_factory(T):
    return np.interp(T, factory_data["T"], factory_data["R"])

PROP_CYCLE = plt.rcParams['axes.prop_cycle']
COLOR_CYCLE = PROP_CYCLE.by_key()['color']


def load_data_means(file_dict, 
                    resistance_key = "resistance",
                    temperature_key = "temp_C",
                    fit_degree = 6
                    ):
    ret = {}
    file_keys = list(file_dict.keys())
    for i in range(len(file_keys)):
        file_key = file_keys[i]
        ret[file_key] = {}
        file_path = file_dict[file_key][0]
        data_dict, device_dict, start_datetime = process_data_from_path(
            file_path, fit_degree=fit_degree, correct_on_sensor_id=False)
        for ch_id in data_dict.keys():
            resistance = data_dict[ch_id][resistance_key]
            temperature = data_dict[ch_id][temperature_key]
            ret[file_key][ch_id] = [np.mean(resistance), np.mean(temperature)]
    return ret, device_dict

def get_ch_ids(means_dict):
    ch_id_list = []
    for file_key in means_dict.keys():
        for ch_id in means_dict[file_key].keys():
            if not(ch_id in ch_id_list):
                ch_id_list.append(ch_id)
    return ch_id_list

def get_means_by_ch_id(means_dict,
                       dataframe_key = "dataframe",
                       resistance_key = "resistance",
                       temperature_key = "temp_C", 
                       measured_temp_key = "Tm",):
    new_dict = {}
    ch_ids = get_ch_ids(means_dict)
    for ch_id in ch_ids:
        new_dict[ch_id] = []
    for Tm in means_dict.keys():
        for ch_id in means_dict[Tm].keys():
            new_dict[ch_id].append([Tm, *means_dict[Tm][ch_id]])
    for ch_id in ch_ids:
        new_dict[ch_id] = {dataframe_key: pandas.DataFrame.from_records(
            np.asarray(new_dict[ch_id]), 
            columns=[measured_temp_key, resistance_key, temperature_key]
            ).sort_values(["resistance"])
            
            }
        
    return new_dict

def calculate_R_of_Tm(dataframe_dict, 
                      dataframe_key = "dataframe", 
                      measured_temp_key = "Tm",
                      R_of_Tm_key = "R_Tm"):
    for key in dataframe_dict.keys():
        dataframe_dict[key][dataframe_key][R_of_Tm_key] = \
            R_of_T_factory(dataframe_dict[key][dataframe_key][measured_temp_key])
    return dataframe_dict

def calculate_fit_parameters(dataframe_dict, 
                      dataframe_key = "dataframe",
                      resistance_key = "resistance",
                      R_of_Tm_key = "R_Tm",
                      fit_params_key = "fit_params",
                      corrected_R_key = "corrected_R",
                      corrected_T_key = "corrected_T",
                      fit_degree = 2,
                      ):
    
    for key in dataframe_dict.keys():
        R_of_Tm = dataframe_dict[key][dataframe_key][R_of_Tm_key]
        resistance = dataframe_dict[key][dataframe_key][resistance_key]
        
        fit_params, fit_cov = polynomial_fit(resistance, R_of_Tm, max_pow = fit_degree, p0=None)
        # print(key, fit_params)
        dataframe_dict[key][fit_params_key] = fit_params
        dataframe_dict[key][dataframe_key][corrected_R_key] = \
            polynomial_variable(resistance, *fit_params)
        dataframe_dict[key][dataframe_key][corrected_T_key] = \
            thermistor_temp_C_from_resistance(dataframe_dict[key][dataframe_key][corrected_R_key])
            
    return dataframe_dict

def get_sensor_ids(device_dict, ch_ids):
    sensor_ids = {}
    pd = pandas.DataFrame.from_records(device_dict["channel_list"])
    for ch_id in ch_ids:
        bs = pd["pin_id"] == ch_id
        if np.sum(bs) < 1:
            raise Exception(f"Missing ch_id {ch_id} in device_dict!")
        elif np.sum(bs) > 1:
            raise Exception(f"Too many entries for ch_id {ch_id} in device_dict!")
        else:
            sensor_ids[ch_id] = pd.loc[bs]["sensor_id"].iloc[0]
    return sensor_ids

def print_sensor_id_compatible_dict(dataframe_dict, sensor_id_dict,
                                    fit_precision = 4):
   
    
    print("CORRECTION_DICT = {")
    for ch_id in temp_dict.keys():
        print_string = f"\t\"{sensor_id_dict[ch_id]}\" : ["
        for fit_param in temp_dict[ch_id]["fit_params"]:
            print_string += f"{fit_param:{fit_precision+7}.{fit_precision}e}, "
        print_string += "],"
        print(print_string)
    print("\t}")

# %%
if __name__ == "__main__":
    # test_file_dict = {
    #     41.3 : ["./thermistor_data/thermistor_test_0016.csv"],
    #     43.0 : ["./thermistor_data/thermistor_test_0013.csv"],
    #     47.6 : ["./thermistor_data/thermistor_test_0015.csv"],
    #     51.0 : ["./thermistor_data/thermistor_test_0014.csv"],
    #     53.3 : ["./thermistor_data/thermistor_test_0017.csv"],
    #     56.9 : ["./thermistor_data/thermistor_test_0012.csv"],
    #     62.3 : ["./thermistor_data/thermistor_test_0018.csv"],
    #     67.6 : ["./thermistor_data/thermistor_test_0020.csv"],
    #     70.5 : ["./thermistor_data/thermistor_test_0019.csv"],
    #     }
    
    test_file_dict = {
        23.9 : ["./thermistor_data/thermistor_02_test_0000.csv"],
        29.3 : ["./thermistor_data/thermistor_02_test_0001.csv"],
        36.4 : ["./thermistor_data/thermistor_02_test_0002.csv"],
        41.0 : ["./thermistor_data/thermistor_02_test_0003.csv"],
        46.1 : ["./thermistor_data/thermistor_02_test_0004.csv"],
        51.5 : ["./thermistor_data/thermistor_02_test_0005.csv"],
        56.5 : ["./thermistor_data/thermistor_02_test_0006.csv"],
        61.3 : ["./thermistor_data/thermistor_02_test_0007.csv"],
        63.9 : ["./thermistor_data/thermistor_02_test_0008.csv"],
        }
    
    ret_dict, device_dict = load_data_means(test_file_dict)
    ch_ids = get_ch_ids(ret_dict)
    sensor_id_dict = get_sensor_ids(device_dict, ch_ids)
    temp_dict = get_means_by_ch_id(ret_dict)
    temp_dict = calculate_R_of_Tm(temp_dict)
    temp_dict = calculate_fit_parameters(temp_dict)
    print_sensor_id_compatible_dict(temp_dict, sensor_id_dict)
    
    # %%
    fig, axes = plt.subplots(nrows=2, ncols=len(ch_ids))
    fig.set_size_inches(np.asarray([1920, 1080])/fig.dpi)
    
    kwargs = {
        "marker":".",
        "ms":5,
        "lw":1
        }
    
    for i in range(len(ch_ids)):
        ch_id = ch_ids[i]
        resistance = temp_dict[ch_id]["dataframe"]["resistance"]
        R_Tm = temp_dict[ch_id]["dataframe"]["R_Tm"]
        temp_C = temp_dict[ch_id]["dataframe"]["temp_C"]
        corrected_R = temp_dict[ch_id]["dataframe"]["corrected_R"]
        corrected_T = temp_dict[ch_id]["dataframe"]["corrected_T"]
        Tm = temp_dict[ch_id]["dataframe"]["Tm"]
        color = COLOR_CYCLE[i%len(COLOR_CYCLE)]
        sensor_id = sensor_id_dict[ch_id]
        
        axes[0, i].plot(resistance, R_Tm, 
                     color=color, 
                     label="Reference",
                     **kwargs, )
        
        axes[0, i].plot(resistance, resistance, 
                     color="k", 
                     label="Measured",
                     **kwargs, )
        
        axes[0, i].plot(resistance, corrected_R, 
                     color="purple", 
                     label="Corrected",
                     **kwargs, )
        
        axes[0, i].legend(loc="upper left")
        axes[0, i].set_xlabel(r"Sensor Resistance [$\Omega$]")
        axes[0, i].set_ylabel(r"Computed Resistance [$\Omega$]")
        
        
        axes[1, i].plot(
            temp_C, Tm,
            color=color,
            label="Reference",
            **kwargs,
            )
        
        axes[1, i].plot(
            temp_C, temp_C,
            color="k",
            label="Measured",
            **kwargs,
            )
        
        axes[1, i].plot(
            temp_C, corrected_T,
            color="purple",
            label="Corrected",
            **kwargs,
            )
        
        
        axes[1, i].legend(loc="upper left")
        axes[1, i].set_xlabel(r"Sensor Temperature [$^\circ$C]")
        axes[1, i].set_ylabel(r"Computed Temperature [$^\circ$C]")
        
        axes[0, i].set_title(f"Sensor {sensor_id}")
        
        
        twinx_0 = axes[0, i].twinx()
        twinx_0.plot(
            resistance, R_Tm - corrected_R,
            color=color,
            **kwargs,
            ls="--",
            label="Correction Error"
            )
        twinx_0.legend(loc="lower right")
        twinx_0.grid(which="both", axis="both")
        axes[0, i].grid(which="both", axis="x")
        
        twinx_1 = axes[1, i].twinx()
        twinx_1.plot(
            temp_C, Tm - corrected_T,
            color=color,
            **kwargs,
            ls="--",
            label="Correction Error"
            )
        twinx_1.legend(loc="lower right")
        twinx_1.grid(which="both", axis="both")
        axes[1, i].grid(which="both", axis="x")
        
        
    fig.suptitle("Thermistor Calibration Check")
    fig.set_tight_layout(True)