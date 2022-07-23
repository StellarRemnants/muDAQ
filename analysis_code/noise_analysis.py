#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 13:05:20 2022

@author: stellarremnants
"""



import numpy as np
import matplotlib.pyplot as plt

from file_read_functions import process_data_from_path

# data_file_path = ("/home/stellarremnants/muDAQ/analysis_code/thermistor_data/kavya_water_bath_calibration/kwbc_0000.csv")
# data_file_path = ("/home/stellarremnants/muDAQ/analysis_code/thermistor_data/joseph_water_bath_calibration/jwbc_0100.csv")
data_file_path = ("/home/stellarremnants/muDAQ/analysis_code/thermistor_data/s"
"olderboard_prototype_water_bath_calibration/sbwbc_0000.csv")

data_dict, device_dict, start_datetime = process_data_from_path(data_file_path, correct_on_sensor_id=False)

keys = list(data_dict.keys())

time_offset = np.min([np.min(data_dict[keys[i]]["TIME"][:10]) for i in range(len(keys))])

fig, axes = plt.subplots(nrows=2)
axes[0].set_xlabel("Time [s]")
axes[0].set_ylabel("Voltage [V]")
axes[1].set_xlabel("Frequency [Hz]")
axes[1].set_ylabel(r"PSD [$\frac{V^2}{Hz}$]")
axes[0].grid()
axes[1].grid()
fig.set_size_inches(np.asarray([1920,1080])/fig.dpi)

for i in range(len(keys)):
    time = (data_dict[keys[i]]["TIME"]-time_offset)*1e-6
    dt = np.mean(np.diff(time))
    voltage = data_dict[keys[i]]["voltage"]
    
    axes[0].plot(time, voltage, label=f"CH {keys[i]}")
    
    fft = np.real(np.fft.rfft(voltage-np.mean(voltage)))
    fftfreq = np.fft.rfftfreq(len(voltage), dt)
    psd = fft**2
    
    axes[1].plot(fftfreq, psd)
    
    rms = (np.mean((voltage - np.mean(voltage))**2))**0.5
    print(f"RMS Noise for CH {keys[i]} : {rms:.6f} V")
    
axes[0].legend()
plt.tight_layout()