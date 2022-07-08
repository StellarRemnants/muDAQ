#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 17:51:59 2022

@author: stellarremnants
"""

from file_read_functions import process_data_from_path



file_list = [
    
    [29.5, 29.9, 29.7, "thermistor_data/00-04_calibration_0001.csv"],
    [34.4, 35.5, 35.6, "thermistor_data/00-04_calibration_0002.csv"],
    [38.3, 39.6, 40.3, "thermistor_data/00-04_calibration_0003.csv"],
    [42.0, 43.7, 45.5, "thermistor_data/00-04_calibration_0004.csv"],
    [46.2, 47.6, 50.8, "thermistor_data/00-04_calibration_0005.csv"],
    [51.3, 65.6, 55.0, "thermistor_data/00-04_calibration_0006.csv"],
    [52.9, 72.1, 60.8, "thermistor_data/00-04_calibration_0007.csv"],
    [56.1, 77.7, 65.8, "thermistor_data/00-04_calibration_0008.csv"],
    ]

for T1, T2, Tc, file_path in file_list:
    
    data_dict, device_dict, start_datetime = process_data_from_path(file_path,
                                                                    correct_on_sensor_id=False)
    