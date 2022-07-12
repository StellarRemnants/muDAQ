#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 14:22:22 2022

@author: stellarremnants
"""

from file_read_functions import process_data_from_path
import numpy as np
import matplotlib.pyplot as plt

file_example = "thermistor_data/00-04_02_calibration_0019.csv"

data_dict_corrected, _, _ = process_data_from_path(
    file_example, correct_on_sensor_id=True
    )

data_dict_uncorrected, _, _ = process_data_from_path(
    file_example, correct_on_sensor_id=False
    )
ch_ids = list(data_dict_corrected.keys())
fig, axes = plt.subplots(nrows=1, ncols=len(ch_ids), sharex=True, sharey=True)

for i in range(len(ch_ids)):
    ch_id = ch_ids[i]
    c_time = data_dict_corrected[ch_id]["TIME"]
    c_temp = data_dict_corrected[ch_id]["temp_C"]
    uc_temp = data_dict_uncorrected[ch_id]["temp_C"]
    # axes[i].plot(c_time, c_temp)
    # axes[i].plot(c_time, uc_temp)
    
    # twinx = axes[i].twinx()
    
    # twinx.plot(c_time, uc_temp-c_temp, color="red")
    axes[i].plot(c_time, uc_temp-c_temp, color="red")
    
fig.set_size_inches(np.asarray([1920, 1080])/fig.dpi)
fig.tight_layout()