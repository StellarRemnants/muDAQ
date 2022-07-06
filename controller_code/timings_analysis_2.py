#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 23 14:18:51 2022

@author: stellarremnants
"""

import pandas
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import mode
from scipy.signal import (
    savgol_filter, find_peaks
    )

def normalize_array(inarray):
    array_min = inarray.min()
    array_max = inarray.max()
    array_span = array_max - array_min
    if array_span > 0:
        return (inarray - array_min) / array_span
    else:
        return inarray
    
def center_array(inarray):
    if len(inarray):
        mean = np.mean(inarray)
    else:
        mean = 0
    return inarray-mean
    
file = "real_data_03.csv"

datapd = pandas.read_csv(file)

ch_array = np.unique(datapd["CH"])

mv_adc_prefactor = 2*2**-14*1000

data_arrays = {}
for ch in ch_array:
    ch_pd = datapd[datapd["CH"]==ch]
    ch_time = np.asarray(ch_pd["TIME"])
    ch_adc = np.asarray(ch_pd["ADC"])
    ch_adc_mv = ch_adc * mv_adc_prefactor
    data_arrays[ch] = [ch_time, ch_adc, ch_adc_mv]
    
    
# fig,ax=plt.subplots()
# for ch in ch_array:
#     mv_mean = data_arrays[ch][2].mean()
#     ax.plot(data_arrays[ch][0], data_arrays[ch][2]-mv_mean)

first_timestamp = np.min([np.min(data_arrays[ch][0][:1]) for ch in ch_array])
for ch in ch_array:
    data_arrays[ch][0] -= first_timestamp
    
if len(ch_array) > 1:
    interchannel_spacing = np.mean(np.diff([data_arrays[ch][0][0] for ch in ch_array]))
else:
    interchannel_spacing = 0
    data_arrays[100] = data_arrays[ch_array[0]]
    ch_array = np.append(ch_array, 100)

diff = np.diff(data_arrays[ch_array[0]][0])
mean_diff = diff.mean()
sample_frequency = 1/(mean_diff*10**-6)
# print(data_arrays[ch_array[0]][0][:20])
print(diff[:20])
print(mean_diff)
print(sample_frequency)
    
ch1 = ch_array[0]; ch2 = ch_array[-1]
d1 = data_arrays[ch1][2]; d1_mean = d1.mean(); t1=data_arrays[ch1][0]
d2 = data_arrays[ch2][2]; d2_mean = d2.mean(); t2=data_arrays[ch2][0]


mt = np.zeros_like(d1, dtype=int)
trange = int(1e4)
modal_range = 0.5

digits = int(np.ceil(np.log10(mt.size)))

for i in range(mt.size):
    frac = (i+1)/mt.size
    print(f"\r{i+1:{digits}d}/{mt.size:{digits}d} ({frac:.1%})",end="")
    lcap = np.max([i-trange, 0])
    hcap = np.min([i+trange, mt.size])
    # print(lcap, hcap)
    temp = abs(t2[lcap:hcap] - t1[i])
    if len(temp):
        mt[i] = np.argmin(temp) + lcap
    else:
        mt[i] = -1
    
q = mt>=0
mt = mt[q]
dt = t2[mt]-t1[q]
dt_mode = mode(dt)[0][0]
nix = np.logical_and(dt<=dt_mode*(1+modal_range), dt>=dt_mode*(1-modal_range))

m1 = d1[q][nix]; tm1 = t1[q][nix];
m2 = d2[mt][nix]; tm2 = t2[mt][nix]



m1_mean = m1.mean(); m1_center = m1-m1_mean;
m2_mean = m2.mean(); m2_center = m2-m2_mean;

sigmas = 2
r1 = abs(np.std(m1_center)) * sigmas
r2 = abs(np.std(m2_center)) * sigmas

s_cond = np.logical_and(abs(m1_center)<r1, abs(m2_center)<r2)

s1=m1_center[s_cond]; tm1 = tm1[s_cond]
s2=m2_center[s_cond]; tm2 = tm2[s_cond]


n1 = normalize_array(s1); c1 = n1-n1.mean()
n2 = normalize_array(s2); c2 = n2-n2.mean()
print()

# %%
savgol_poly = 0
savgol_window_fraction = 10
savgol_repeat = 5

fig, ax = plt.subplots()
ax.plot(tm1, c1)

slice_y = c1
savgol_window = int(slice_y.size/savgol_window_fraction)
if savgol_window %2 == 0:
    savgol_window += 1
for i in range(savgol_repeat):
    print(f"\r{i+1}/{savgol_repeat}",end="")
    temp_savgol_window = int(savgol_window//(i+1))
    if temp_savgol_window <= savgol_poly:
        temp_savgol_window = savgol_poly + 1
    if temp_savgol_window %2 == 0:
        temp_savgol_window += 1
    slice_y = savgol_filter(slice_y, temp_savgol_window, savgol_poly, mode="wrap")
    # temp_slice = center_array(normalize_array(slice_y))
    temp_slice = slice_y
    ax.plot(tm1, temp_slice, label=f"window: {temp_savgol_window}, i:{i}")
slice_y = normalize_array(slice_y)
slice_y = center_array(slice_y)

ax.legend()
print()

# %%
savgol_poly = 0
savgol_window_fraction = 50
savgol_repeat = 10

sav1 = c1; sav2 = c2
for i in range(savgol_repeat):
    print(f"\r{i+1}A/{savgol_repeat}",end="")
    savgol_window_1 = int(c1.size/savgol_window_fraction/(i+1))
    if savgol_window_1 %2 == 0:
        savgol_window_1 += 1 
    sav1 = savgol_filter(sav1, savgol_window_1, savgol_poly, mode="wrap")
    
    print(f"\r{i+1}B/{savgol_repeat}",end="")
    savgol_window_2 = int(c2.size/savgol_window_fraction)
    if savgol_window_2 %2 == 0:
        savgol_window_2 += 1 
    sav2 = savgol_filter(sav2, savgol_window_2, savgol_poly, mode="wrap")

sav1 = center_array(normalize_array(sav1))
sav2 = center_array(normalize_array(sav2))
print()
# %%
fig,ax=plt.subplots()
ax.plot(tm1, sav1, marker=".", ms=1)
ax.plot(tm2, sav2, marker=".", ms=1)

# %%
compression_factor = 50
num_points = np.max([t1.size, t2.size])//compression_factor
time_range = np.linspace(0, np.max([t1.max(), t2.max()]), num_points)
time_delta = time_range[1]
time_average_1 = np.zeros_like(time_range)
time_average_2 = np.zeros_like(time_average_1)

time_1 = 0
time_2 = time_delta

digits = int(np.ceil(np.log10(time_range.size)))
for i in range(time_range.size):
    print(f"\r{i+1:{digits}d}/{time_range.size:{digits}d} ({(i+1)/(time_range.size):.1%})", end="")
    cond1 = np.logical_and(t1 >= time_1, t1 < time_2)
    cond2 = np.logical_and(t2 >= time_1, t2 < time_2)
    
    d1_c = d1[cond1]
    d2_c = d2[cond2]
    if len(d1_c):
        time_average_1[i] = np.mean(d1[cond1])
    else:
        time_average_1[i] = np.nan
    
    if len(d2_c):
        time_average_2[i] = np.mean(d2[cond2])
    else:
        time_average_2[i] = np.nan
    
    time_1 += time_delta
    time_2 += time_delta
    
print()
# %%

fig, ax = plt.subplots()
ax.plot(time_range, time_average_1)
ax.plot(time_range, time_average_2)