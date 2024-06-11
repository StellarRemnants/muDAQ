#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 13:46:02 2024

@author: stellarremnants
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
import datetime
import os

def load_preamble(fdin, read_until="`---`"):
    time_lines = []
    preamble_lines = []
    # fdin =  open(csv_file_path, "r")
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
    
    # print(preamble_lines)
    program_dict = json.loads("\n".join(preamble_lines))
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
                
    
    return fdin, start_datetime, program_dict

def separate_channels(dataframe):
    channel_ids = np.unique(dataframe["CH"])
    data_dict = {}
    for ch_id in channel_ids:
        channel_bool = dataframe["CH"] == ch_id
        sliced_dataframe = dataframe[channel_bool]
        data_dict[ch_id] = sliced_dataframe.reset_index(drop=True)
        
    return data_dict

def concatenate_dataframes(df1, df2, sort_by=None, ignore_index=True):
    df = pd.concat([df1, df2], ignore_index=ignore_index) 
    if not(sort_by is None):
        df.sort_values(sort_by, inplace=True)
    return df

def rotate_dataframes(df1, df2, sort_by="COMPTIME", keep_points = 100):
    df = concatenate_dataframes(df1, df2, sort_by=sort_by)
    return df.iloc[-keep_points:]

def rescale_axis(ax, margins=[0,0.05]):
    lines = list(ax.lines)
    xbound=[None,None]
    ybound=[None,None]
    for line in lines:
        x,y = line.get_data()
        xmin = np.min(x); xmax = np.max(x)
        ymin = np.min(y); ymax = np.max(y)
        if xbound[0] is None:
            xbound[0] = xmin
        if xbound[1] is None:
            xbound[1] = xmax
        if ybound[0] is None:
            ybound[0] = ymin
        if ybound[1] is None:
            ybound[1] = ymax
            
        if xmin < xbound[0]:
            xbound[0] = xmin
        if xmax > xbound[1]:
            xbound[1] = xmax
        if ymin < ybound[0]:
            ybound[0] = ymin
        if ymax > ybound[1]:
            ybound[1] = ymax
            
    xrange = xbound[1] - xbound[0]
    yrange = ybound[1] - ybound[0]
    
    xlim = [xbound[0]-margins[0]*xrange, xbound[1]+margins[0]*xrange]
    ylim = [ybound[0]-margins[1]*yrange, ybound[1]+margins[1]*yrange]
    
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    
def convert_ADC_to_voltage(adc_values, max_voltage, bit_resolution):
    return adc_values * max_voltage / 2**bit_resolution


if __name__ == "__main__":
    
    data_directory = "/home/stellarremnants/muDAQ_data/displacement_sensor_data/"
    
    data_filename = "displacement_sensor_noise_run__0000.csv"
    
    data_path = os.path.join(data_directory, data_filename)
    
    with open(data_path, "r") as fd_data_in:
        fdin, start_datetime, program_dict = load_preamble(fd_data_in)
        df = pd.read_csv(fdin)
        
    # %%
    time_arr = np.asarray(df["COMPTIME"]) - start_datetime.timestamp()
    
    data_arr = df["ADC"]
    
    max_volt = program_dict["device_list"][0]["max_voltage"]
    bit_res = program_dict["device_list"][0]["bit_resolution"]
    
    volt_arr = data_arr * max_volt / (2**bit_res)
    
    fft_arr = np.real(np.fft.rfft(volt_arr-np.mean(volt_arr)))
    fft_freq = np.fft.rfftfreq(len(volt_arr), np.mean(np.diff(time_arr)))
    
    fig, ax = plt.subplots()
    # ax.plot(fft_freq, fft_arr**2)
    ax.plot(time_arr, volt_arr)