#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 15:31:25 2023

@author: stellarremnants
"""

import paramiko
import pandas
from io import StringIO
import json
import datetime
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


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
    
    print(preamble_lines)
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
    df = pandas.concat([df1, df2], ignore_index=ignore_index) 
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

def convert_voltage_to_resistance(voltage, ref_resistance, ref_voltage):
    return ref_resistance / (ref_voltage/voltage - 1)
    
def plot_line(ax, data_dict, channel, program_dict, start_time, plot_val="resistance", **kwargs):
    max_voltage = program_dict["device_list"][0]["max_voltage"]
    bit_resolution = program_dict["device_list"][0]["bit_resolution"]
    
    channel_list = program_dict["device_list"][0]["channel_list"]
    channel_dict = {}
    for ch in channel_list:
        channel_dict[ch["pin_id"]] = ch
    if not(channel in list(channel_dict.keys())):
        raise KeyError(f"Unable to find channel '{channel}' in list of channels")
    else:
        ref_resistance = channel_dict[channel]["ref_resistance"]
        ref_voltage = channel_dict[channel]["ref_voltage"]
    
    
    channel_name = channel_dict[channel]["channel_name"]
    label = f"Device 0 : Channel {channel}\n{channel_name}"
    
    adc = data_dict[channel]["ADC"]
    voltage = convert_ADC_to_voltage(adc, max_voltage, bit_resolution)
    resistance = convert_voltage_to_resistance(voltage, ref_resistance, ref_voltage)
    
    
    if plot_val.lower() == "resistance":
        val = resistance
    elif plot_val.lower() == "voltage":
        val = voltage
    elif plot_val.lower() == "adc":
        val = adc
    else:
        val = voltage
    
    
    line = ax.plot(data_dict[channel]["COMPTIME"]-start_time, 
                   val,
            label=label, **kwargs)[0]
    
    return line

def modify_data(data_dict, channel, lines, program_dict, start_time, plot_val="resistance"):
    max_voltage = program_dict["device_list"][0]["max_voltage"]
    bit_resolution = program_dict["device_list"][0]["bit_resolution"]
    
    channel_list = program_dict["device_list"][0]["channel_list"]
    channel_dict = {}
    for ch in channel_list:
        channel_dict[ch["pin_id"]] = ch
    if not(channel in list(channel_dict.keys())):
        raise KeyError(f"Unable to find channel '{channel}' in list of channels")
    else:
        ref_resistance = channel_dict[channel]["ref_resistance"]
        ref_voltage = channel_dict[channel]["ref_voltage"]
    
    adc = data_dict[channel]["ADC"]
    voltage = convert_ADC_to_voltage(adc, max_voltage, bit_resolution)
    resistance = convert_voltage_to_resistance(voltage, ref_resistance, ref_voltage)
    
    
    
    line = lines[channel]
    
    if plot_val.lower() == "resistance":
        val = resistance
    elif plot_val.lower() == "voltage":
        val = voltage
    elif plot_val.lower() == "adc":
        val = adc
    else:
        val = voltage
        
    line.set_data(data_dict[channel]["COMPTIME"]-start_time, val)
    
def reset_legend(ax, anchor_tuple=(1.25, 0.95), **legend_kwargs):
    ax.legend(bbox_to_anchor=anchor_tuple, loc="center", **legend_kwargs)
    
def connect_to_client(host, username, password=None):
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=username, password=password)
    
    return client

def connect_client_sftp(client):
    sftp = client.open_sftp()
    return sftp

def file_open_for_read(file_path):
    fdin = open(file_path, "r")
    return fdin

def close_connection(client, fdin):
    fdin.close()
    client.close()
    
def initial_file_load(
        fdin, 
        skip_bulk, 
        init_seek, 
        plot_last_points, 
        program_dict,
        file_path
                      ):
    
    if not skip_bulk:
        init_read = fdin.read().decode()
    else:
        init_read = fdin.read(init_seek)
        init_split = init_read.split("\n")
        line_size = max([len(init_split[i]) for i in range(len(init_split))])
        init_read = "\n".join(init_split[:-1])
        starting_offset = (line_size+2) * plot_last_points * sum(
            [len(program_dict["device_list"][i]["channel_list"]) for i in range(
                len(program_dict["device_list"]))
                ] * 2
            )
        
    if len(init_read):
        init_df = pandas.read_csv(StringIO(init_read))
        columns = init_df.columns
    else:
        raise Exception(f"File is empty! '{file_path}'")
    init_data_dict = separate_channels(init_df)
    
    data_dict = {}
    channels = list(init_data_dict.keys())
    for channel in channels:
        data_dict[channel] = init_data_dict[channel].iloc[-plot_last_points:]
        
    del(init_df, init_data_dict, init_read)
    
    if skip_bulk:
        # fdin.seek(-starting_offset, 2)
        pos = fdin.tell()
        if pos < 0:
            fdin.seek(0,2)
        rl = " "
        while len(rl) and rl != "\n":
            rl = fdin.read(1)
    
    return columns, channels, data_dict, program_dict

def live_plotter_loop(
        fdin, 
        columns, 
        channels, 
        data_dict, 
        plot_last_points,
        lines,
        ax,
        program_dict,
        anchor,
        margins,
        refresh_period,
        fig,
        start_time,
        plot_val="resistance"
        ):
    
    try:
        while True:
            read_data = fdin.read()
            if len(read_data):
                read_df = pandas.read_csv(StringIO(read_data), names=columns)
                read_data_dict = separate_channels(read_df)
                read_channels = list(read_data_dict.keys())
                for rchan in read_channels:
                    if not(rchan in channels):
                        data_dict[rchan] = read_data_dict[rchan].iloc[-plot_last_points:]
                    else:
                        data_dict[rchan] = rotate_dataframes(
                            data_dict[rchan], 
                            read_data_dict[rchan],
                            keep_points=plot_last_points
                            )
                    if not(rchan in list(lines.keys())):
                        lines[rchan] = plot_line(ax, data_dict, rchan, program_dict, start_time)
                        reset_legend(ax, anchor_tuple=anchor)
                    else:
                        modify_data(data_dict, rchan, lines, program_dict, start_time, plot_val)
                rescale_axis(ax, margins=margins)
            plt.pause(refresh_period)
            if not(plt.fignum_exists(fig.number)):
                break
    except KeyboardInterrupt:
        pass
    
def live_plot_setup(
        formatter, 
        channels, 
        data_dict, 
        program_dict, 
        anchor, 
        margins,
        res,
        username,
        host,
        file_path,
        start_time,
        box_width = 0.85,
        box_height = 1.00,
        plot_val="resistance"
        ):
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(formatter)
    lines = {}
    for channel in channels:
        lines[channel] = plot_line(ax, data_dict, channel, program_dict, start_time, plot_val)
        
    ax.grid()
    ax.set_xlabel("Time elapsed [hh:mm:ss]")
    
    if plot_val.lower() == "resistance":
        ax.set_ylabel("Resistance [Ohms]")
    elif plot_val.lower() == "voltage":
        ax.set_ylabel("Voltage [V]")
    elif plot_val.lower() == "adc":
        ax.set_ylabel("ADC [bit]")
    else:
        ax.set_ylabel("Voltage [V]")
    
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * box_width, box.height * box_height])
    
    # ax.legend(bbox_to_anchor=(1.25, 0.95))
    reset_legend(ax, anchor_tuple=anchor)
    rescale_axis(ax, margins=margins)
    fig.set_size_inches(np.asarray(res)/fig.dpi)
    fig.suptitle(f"Source: {username}@{host}\n'{file_path}'")
    
    return fig, ax, lines


def formatter_fnc():
    def format_func(x, pos):
        hours = int(x//3600)
        minutes = int((x%3600)//60)
        seconds = int(x%60)
        if hours > 0:
            return f"{hours}h{minutes:02d}m{seconds:02d}s"
        elif minutes > 0:
            return f"{minutes:02d}m{seconds:02d}s"
        else:
            return f"{seconds:02d}s"
    
    formatter = FuncFormatter(format_func)
    
    return formatter