#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 13:13:40 2022

@author: stellarremnants
"""

import pandas
import numpy as np
import json
import datetime

from thermistor_correction_library import correct_resistance

FIT_DICT = {
    "micro_betachip":{
        0:[42.5],
        1:[252.94145479, -24.06575193], 
        2:[380.77306453, -53.69746749,   1.63343464],
        3:[ 4.62556894e+02, -8.21852677e+01,  4.84010657e+00, -1.16844917e-01],
        4:[ 5.15530422e+02, -1.06797548e+02,  9.03384774e+00, -4.27620978e-01,
            8.45963583e-03],
        5:[ 5.49667756e+02, -1.26625041e+02,  1.35610792e+01, -9.35715730e-01,
            3.65019300e-02, -6.09276640e-04],
        6:[ 5.72172989e+02, -1.42310736e+02,  1.80521266e+01, -1.61192675e+00,
            9.29883264e-02, -3.09222662e-03,  4.48890480e-05],
        7:[ 5.93759975e+02, -1.59863646e+02,  2.40959658e+01, -2.75433403e+00,
            2.21033659e-01, -1.16043492e-02,  3.55732332e-04, -4.81185545e-06],
        },
    "amphenol":{
        0: [49.1025641],
        1: [261.33981361, -24.58451762],
        2: [389.00067675, -55.05893299,   1.68321976],
        3: [ 4.72477447e+02, -8.48720309e+01,  5.06409149e+00, -1.22350588e-01],
        4: [ 5.25274128e+02, -1.10045539e+02,  9.41496800e+00, -4.45883405e-01,
            8.75318294e-03],
        5: [ 5.59182551e+02, -1.30316960e+02,  1.41348196e+01, -9.81153026e-01,
            3.83539491e-02, -6.39514477e-04],
        6: [ 5.78410736e+02, -1.44074320e+02,  1.81477170e+01, -1.59219905e+00,
            8.96161783e-02, -2.88798655e-03,  4.03248781e-05],
        7: [ 5.76612813e+02, -1.42571032e+02,  1.76187325e+01, -1.49063195e+00,
            7.81201682e-02, -2.12055542e-03,  1.23305815e-05,  4.30755931e-07],
        8: [ 5.96778701e+02, -1.61862994e+02,  2.55662385e+01, -3.33228597e+00,
            3.40736974e-01, -2.57263154e-02,  1.31903377e-03, -4.03160130e-05,
            5.48296082e-07],
        9: [ 8.62865244e-01,  4.74725687e+02, -2.72468757e+02,  7.69401608e+01,
           -1.33695492e+01,  1.51464061e+00, -1.12560833e-01,  5.30393967e-03,
           -1.43971693e-04,  1.71656200e-06]
         },
    }

def ln_fit_variable(R, *args):
    log_R = np.log(R)
    dat = np.zeros_like(log_R)
    
    for i in range(len(args)):
        dat += args[i] * log_R ** i
    return dat
    

def load_preamble(csv_file_path, read_until="`---`"):
    time_lines = []
    preamble_lines = []
    fdin =  open(csv_file_path, "r")
    readline = ""
    ru_len = len(read_until)
    while True:
        readline = fdin.readline()
        if readline[:ru_len] == read_until:
            break
        elif not len(readline):
            break
        else:
            while (readline[-1] == "\n" or readline[-1] == "\r"):
                readline = readline[:-1]
            time_lines.append(readline)
        
    while True:
        readline = fdin.readline()
        if readline[:ru_len] == read_until:
            break
        elif not len(readline):
            break
        else:
            while (readline[-1] == "\n" or readline[-1] == "\r"):
                readline = readline[:-1]
            preamble_lines.append(readline)
    
    device_dict = json.loads("\n".join(preamble_lines))
    timestamp = None
    for tl in time_lines:
        tls = tl.split(",")
        if len(tls) >= 2:
            if tls[0] == "UTC timestamp":
                timestamp = float(tls[1])
    if not (timestamp is None):
        start_datetime = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
    else:
        start_datetime = None
                
    
    return fdin, start_datetime, device_dict
            
def load_dataframe(fdin):
    return pandas.read_csv(fdin)

def adc_to_voltage(dataframe, max_voltage, bit_resolution):
    return dataframe.assign(voltage = dataframe["ADC"] * max_voltage / 2**bit_resolution)

def thermisor_resistance_from_voltage(voltage_array, ref_resistance, ref_voltage):
    return ref_resistance * voltage_array / (ref_voltage- voltage_array)

def thermistor_temp_C_from_resistance(resistance, fit_degree=6, thermistor_type="micro_betachip"):
    if thermistor_type == "unknown":
        return resistance
    else:
        return ln_fit_variable(resistance, *FIT_DICT[thermistor_type][fit_degree])

def separate_channels(dataframe):
    channel_ids = np.unique(dataframe["CH"])
    data_dict = {}
    for ch_id in channel_ids:
        channel_bool = dataframe["CH"] == ch_id
        sliced_dataframe = dataframe[channel_bool]
        data_dict[ch_id] = sliced_dataframe.reset_index(drop=True)
        
    return data_dict

def process_data_from_path(data_file_path,
                           fit_degree = 6,
                           correct_on_sensor_id = True,
                           ):
    fdin, start_datetime, device_dict = load_preamble(data_file_path)
    dataframe = load_dataframe(fdin)
    fdin.close()
    
    dataframe = adc_to_voltage(dataframe, device_dict["max_voltage"], device_dict["bit_resolution"])
    data_dict = separate_channels(dataframe)
    channel_settings = {}
    for channel_dict in device_dict["channel_list"]:
        ch_id = channel_dict["pin_id"]
        channel_settings[ch_id] = channel_dict
        
    for ch_id in channel_settings.keys():
        if ch_id in data_dict.keys():
            sensor_type = channel_settings[ch_id]["sensor_type"].lower()
            if sensor_type == "thermistor":
                thermistor_type = channel_settings[ch_id]["thermistor_type"].lower()
                cond = data_dict[ch_id]["voltage"] > 0
                data_dict[ch_id] = data_dict[ch_id].loc[cond]
                resistance = thermisor_resistance_from_voltage(data_dict[ch_id]["voltage"], 
                                                               channel_settings[ch_id]["ref_resistance"], 
                                                               channel_settings[ch_id]["ref_voltage"])
                if correct_on_sensor_id:
                    sensor_id = channel_settings[ch_id]["sensor_id"]
                    if sensor_id.lower() != "unknown":
                        resistance = correct_resistance(resistance, sensor_id)
                data_dict[ch_id] = data_dict[ch_id].assign(resistance=resistance).reset_index(drop=True)
                temp_C = thermistor_temp_C_from_resistance(resistance, 
                                                           fit_degree=fit_degree, 
                                                           thermistor_type=thermistor_type)
                data_dict[ch_id] = data_dict[ch_id].assign(temp_C=temp_C).reset_index(drop=True)
            else:
                raise NotImplementedError(f"Analysis for sensor_type \"{sensor_type}\" is not yet implemented")
                
    return data_dict, device_dict, start_datetime
    

# %%

if __name__ == "__main__":
    data_file_path = (
        "./thermistor_data/thermistor_02_test_0008.csv"
        )
    data_dict, device_dict, start_datetime = process_data_from_path(data_file_path)