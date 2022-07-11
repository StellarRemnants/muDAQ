#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 13:05:20 2022

@author: stellarremnants
"""



import numpy as np
import matplotlib.pyplot as plt

from file_read_functions import process_data_from_path

data_file_path = "thermistor_data/noise_examination_0002.csv"

data_dict, device_dict, start_datetime = process_data_from_path(data_file_path)

keys = list(data_dict.keys())

time_offset = np.min([np.min(data_dict[keys[i]]["TIME"][:10]) for i in range(len(keys))])

fig, axes = plt.subplots(nrows=2)

for i in range(len(keys)):
    time = (data_dict[keys[i]]["TIME"]-time_offset)*1e-6
    dt = np.mean(np.diff(time))
    voltage = data_dict[keys[i]]["voltage"]
    
    axes[0].plot(time, voltage)
    
    fft = np.real(np.fft.rfft(voltage-np.mean(voltage)))
    fftfreq = np.fft.rfftfreq(len(voltage), dt)
    psd = fft**2
    
    axes[1].plot(fftfreq, psd)