#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 14 09:27:16 2022

@author: stellarremnants
"""

import pandas
import numpy as np

file = "test4.csv"

# datapd = pandas.read

datapd = pandas.read_csv(file)

ch_array = np.unique(datapd["CH"])

mv_adc_prefactor = 5*2**-10*1000

data_arrays = {}
for ch in ch_array:
    ch_pd = datapd[datapd["CH"]==ch]
    ch_time = np.asarray(ch_pd["TIME"])
    ch_adc = np.asarray(ch_pd["ADC"])
    ch_adc_mv = ch_adc * mv_adc_prefactor
    data_arrays[ch] = (ch_time, ch_adc, ch_adc_mv)
    
for ch in ch_array:
    file_name = f"{file}.{ch}.csv"
    ch_time, ch_adc, ch_adc_mv = data_arrays[ch]
    with open(file_name, "w") as fdout:
        fdout.write("TIME,ADC,ADC_MV\n")
        for i in range(ch_time.size):
            fdout.write(f"{ch_time[i]:d},{ch_adc[i]:d},{ch_adc_mv[i]: 5.3f}\n")