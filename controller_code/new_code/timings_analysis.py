#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 12 17:18:49 2022

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
# %%
file = "therm_test_11.csv"

datapd = pandas.read_csv(file)

ch_array = np.unique(datapd["CH"])

max_volt = 2
resolution = 14
mv_adc_prefactor = max_volt*2**-resolution*1000

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
trange = int(1e3)
modal_range = 0.5
for i in range(mt.size):
    lcap = np.max([i-trange, 0])
    hcap = np.min([i+trange, mt.size])
    # print(lcap, hcap)
    temp = abs(t2[lcap:hcap] - t1[i])
    if len(temp):
        mt[i] = np.argmin(temp) + lcap
    else:
        mt[i] = t2.size-1
    
dt = t2[mt]-t1
dt_mode = mode(dt)[0][0]
if dt_mode < 0:
    dt_mode = -dt_mode
    dt = -dt
nix = np.logical_and(dt<=dt_mode*(1+modal_range), dt>=dt_mode*(1-modal_range))

m1 = d1[nix]; tm1 = t1[nix];
m2 = d2[mt][nix]; tm2 = t2[mt][nix]



m1_mean = m1.mean(); m1_center = m1-m1_mean;
m2_mean = m2.mean(); m2_center = m2-m2_mean;

sigmas = 2
r1 = abs(np.std(m1_center)) * sigmas
r2 = abs(np.std(m2_center)) * sigmas

s_cond = np.logical_and(abs(m1_center)<=r1, abs(m2_center)<=r2)

s1=m1_center[s_cond]; tm1 = tm1[s_cond]
s2=m2_center[s_cond]; tm2 = tm2[s_cond]


n1 = normalize_array(s1); c1 = n1-n1.mean()
n2 = normalize_array(s2); c2 = n2-n2.mean()

downsample_rate = 1
c1 = c1[::downsample_rate]
c2 = c2[::downsample_rate]
tm1 = tm1[::downsample_rate]
tm2 = tm2[::downsample_rate]
sample_spacing_mus = np.diff(tm1).mean()
sample_spacing_s = sample_spacing_mus * 10**-6


dt_tolerance = 1e6

d1_cond = np.abs(np.concatenate(([0],np.diff(t1)))) < dt_tolerance
d2_cond = np.abs(np.concatenate(([0],np.diff(t2)))) < -dt_tolerance
# d1_cond = (d1.max()-d1.min())
d1_cond = np.logical_not(d1_cond)
d2_cond = np.logical_not(d2_cond)

fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True)

kwargs = {"ms" : 2, "marker" : ".", "ls" : "-", "lw" : 1}

ax[0].plot(t1[d1_cond]*1e-6, d1[d1_cond], color="blue", **kwargs)
ax[1].plot(tm1*1e-6, c1, color="lightblue", **kwargs)
ax[0].plot(t2[d2_cond]*1e-6, d2[d2_cond], color="red", **kwargs)
ax[1].plot(tm2*1e-6, c2, color="pink", **kwargs)

#%%
fig, ax = plt.subplots()
data_1 = data_arrays[ch1][1]
data_2 = data_arrays[ch2][1]
min_size = np.min([data_1.size, data_2.size])
skip_first = int(min_size/10)
skip_first = 0
ax.plot(d1[skip_first:min_size], d2[skip_first:min_size], marker=".", ms=3, lw=0)
# ax.plot(data_1[skip_first:min_size], data_2[skip_first:min_size], marker=".", ms=3, lw=0)

#%%
fft1 = np.fft.rfft(d1-d1.mean())
freq1 = np.fft.fftfreq(fft1.size, d=np.diff(t1).mean()*10**-6)
fft2 = np.fft.rfft(d2-d2.mean())
freq2 = np.fft.fftfreq(fft2.size, d=np.diff(t2).mean()*10**-6)

window_fraction = 1000
savgol_window_1 = int(d1.size//window_fraction); savgol_window_2 = int(d2.size//window_fraction); 
if savgol_window_1 % 2 == 0:
    savgol_window_1 += 1
if savgol_window_2 % 2 == 0:
    savgol_window_2 += 1
poly_order = 0

cond1 = freq1 >= 0
cond2 = freq2 >= 0

a1 = abs(np.real(fft1))
a2 = abs(np.real(fft2))
f1 = savgol_filter(a1, savgol_window_1, poly_order)
f2 = savgol_filter(a2, savgol_window_2, poly_order)

fig,ax=plt.subplots(nrows=2, sharex=True)
ax[0].plot(freq1[cond1], a1[cond1])
ax[0].plot(freq1[cond1], f1[cond1])

ax[1].plot(freq2[cond2], a2[cond2])
ax[1].plot(freq2[cond2], f2[cond2])

# %%
signal_1 = c1
signal_2 = c2
num_1 = signal_1.size
num_2 = signal_2.size
min_num = np.min([num_1, num_2])
window_size = min_num//16
# window_size = 500

search_time_min = -5
search_time_max = 5
search_arg_min = search_time_min / sample_spacing_s
search_arg_max = search_time_max / sample_spacing_s

num_1_range = np.arange(0, num_1-window_size)
num_2_range = np.arange(0, num_2-window_size)

rmax_1 = num_1_range.size
rmax_2 = num_2_range.size

correlation_coefficients = np.zeros([rmax_1, rmax_2], dtype=float)

dplaces_1 = int(np.ceil(np.log10(rmax_1)))

for start_1 in num_1_range:
    print(f"\rSingal 1 ({start_1+1:0{dplaces_1}d}/{rmax_1}) "
          f"[{(start_1+1)/rmax_1:.1%}]", end="")
    check_min = np.max([0, start_1 + search_arg_min])
    check_max = np.min([rmax_2, start_1 + search_arg_max])
    check_range = num_2_range[np.logical_and(
        num_2_range >= check_min,
        num_2_range <= check_max
        )]
    sig1 = signal_1[start_1:start_1+window_size]
    sig1 = normalize_array(sig1)
    sig1 = sig1-sig1.mean()
    for start_2 in check_range:
        sig2 = signal_2[start_2:start_2+window_size]
        sig2 = normalize_array(sig2)
        sig2 = sig2-sig2.mean()
        corr = np.correlate(sig1, sig2)
        correlation_coefficients[start_1, start_2] = corr
#%%

delay_args = np.zeros(rmax_1, dtype = float)
slice_x = np.arange(0, rmax_2)
search_width = int((search_arg_max - search_arg_min)/4)
peak_distance = search_width
fig,ax=plt.subplots()

peak_array = np.zeros_like(delay_args)

# compare_len = 10
plot_count = 25
plot_every = rmax_1 // plot_count

# savgol_window = 20
savgol_poly = 1
centering_coeff = 0
centering_power = 0
savgol_window_fraction = 100
savgol_repeat = 5
plot_counter = 0

trim_start = abs(int((search_time_max-search_time_min)/sample_spacing_s))
trim_end = -trim_start

for start_1 in num_1_range:
    
    
    check_min = np.max([0, start_1 + search_arg_min])
    check_max = np.min([rmax_2, start_1 + search_arg_max])
    check_range = num_2_range[np.logical_and(
        num_2_range >= check_min,
        num_2_range <= check_max
        )]
    
    slice_y = correlation_coefficients[start_1, check_range]
    savgol_window = int(slice_y.size/savgol_window_fraction)
    if savgol_window %2 == 0:
        savgol_window += 1
    for i in range(savgol_repeat):
        temp_savgol_window = int(savgol_window//(i+1))
        if temp_savgol_window <= savgol_poly:
            temp_savgol_window = savgol_poly + 1
        if temp_savgol_window %2 == 0:
            temp_savgol_window += 1
        slice_y = savgol_filter(slice_y, temp_savgol_window, savgol_poly)
    slice_y = normalize_array(slice_y)
    slice_y = slice_y/(
        1+centering_coeff*\
            abs((check_range-(check_max+check_min)/2)/\
                (check_max-check_min))**centering_power
        )
    max_arg = np.argmax(slice_y) 
    peaks, _ = find_peaks(slice_y, distance=slice_y.size)
    if len(peaks):
        peak_arg = peaks[0]
    else:
        peak_arg = max_arg
    # peak_array[start_1] = peak_arg
    delay_args[start_1] = start_1 - check_range[peak_arg]
    
    if start_1 % plot_every == 0:
        ax.plot(check_range*sample_spacing_s, slice_y)
        ax.plot(check_range[peak_arg]*sample_spacing_s, slice_y[peak_arg], marker="x", color="red")
        print(f"\rPlot Count: {plot_counter+1}/{plot_count}", end="")
        plot_counter += 1

delay_times = delay_args * sample_spacing_s
mean_delay = np.mean(delay_times[trim_start:trim_end])
mean_arg = np.mean(delay_args[trim_start:trim_end])
fig.suptitle("Peak Sensing Quality Check")
# %%
# slice_x = np.arange(0, rmax_2)
# search_width = int((search_arg_max - search_arg_min)/4)
# peak_distance = search_width
fig,ax=plt.subplots()

start_1 = int(1e3)
savgol_poly = 1
centering_coeff = 0
centering_power = 3
# savgol_repeat = 0
savgol_window_fraction = 20

# for centering_coeff in np.asarray([0, 1, 2, 5, 10]):
# for savgol_poly in np.asarray([0,1,2,3,4,5]):
for savgol_repeat in np.asarray([0,1,2,3,4,5]):
    
    plot_counter = 0
    start_1 = 10000
    check_min = np.max([0, start_1 + search_arg_min])
    check_max = np.min([rmax_2, start_1 + search_arg_max])
    check_range = num_2_range[np.logical_and(
        num_2_range >= check_min,
        num_2_range <= check_max
        )]
    
    slice_y = correlation_coefficients[start_1, check_range]
    savgol_window = int(slice_y.size/savgol_window_fraction)
    for i in range(savgol_repeat):
        temp_savgol_window = int(savgol_window//(i+1))
        if temp_savgol_window <= savgol_poly:
            temp_savgol_window = savgol_poly + 1
        if temp_savgol_window %2 == 0:
            temp_savgol_window += 1
        slice_y = savgol_filter(slice_y, temp_savgol_window, savgol_poly)
    slice_y = normalize_array(slice_y)
    slice_y = slice_y/(
        1+centering_coeff*\
            (abs(check_range-(check_max+check_min)/2)/\
                (check_max-check_min))**centering_power
        )
    slice_y = normalize_array(slice_y)
    max_arg = np.argmax(slice_y) 
    peaks, _ = find_peaks(slice_y, distance=slice_y.size)
    if len(peaks):
        peak_arg = peaks[0]
    else:
        peak_arg = max_arg
    ax.plot(check_range*sample_spacing_s, slice_y, label=f"coeff: {centering_coeff}")
    ax.plot(check_range[peak_arg]*sample_spacing_s, slice_y[peak_arg], marker="x", color="red")
# %%
fig,(ax1d, ax2d)=plt.subplots(nrows=1, ncols=2)
fig.set_size_inches(np.asarray([1920,1080])/fig.dpi)
ax2d.imshow(correlation_coefficients.T,
          origin="lower",
          interpolation="None")

# for start_1 in num_1_range:
ax2d.plot(num_1_range[trim_start:trim_end], 
          (num_1_range - delay_args)[trim_start:trim_end],
          color="red", marker=".", label="Maxima")
ax2d.plot(num_1_range, num_1_range, color="cyan", label="0 delay")
ax2d.plot(num_1_range+ mean_arg, num_1_range , color="orange", label=f"Mean Delay {mean_delay:.3f}")
# ax2d.plot(num_1_range+ shift_2/sample_spacing, num_1_range , color="black", label=f"Input Delay {shift_2:.3f}")
ax2d.legend()

ax1d.set_xlabel("Signal 1 Index")
ax1d.set_ylabel("Signal 2 Index")


ax1d.plot(num_1_range[trim_start:trim_end]*sample_spacing_s, 
          delay_times[trim_start:trim_end],
          label="Delay Times")
ax1d.plot(num_1_range*sample_spacing_s, np.ones_like(num_1_range)*mean_delay, color="orange", 
          label=f"Mean Delay {mean_delay:.3f}")
# ax1d.plot(num_1_range, np.ones_like(num_1_range)*shift_2, color="black", 
#           label=f"Input Delay {shift_2:.3f}")
ax1d.legend()

ax1d.set_xlabel("Signal 1 Index")
ax1d.set_ylabel("Delay")
fig.suptitle("Time Series Window Results")

# %%
delay_cond = abs(delay_times) < 10

x = np.arange(delay_times.size)
fig, ax = plt.subplots()

s = savgol_filter(delay_times[delay_cond], 101, 0)

ax.plot(x, delay_times)
ax.plot(x[delay_cond], delay_times[delay_cond])
ax.plot(x[delay_cond], s)

separation = 2.54 #cm
speed = separation/abs(s)
speed_cond = abs(speed) < 1000
speed_range = x[delay_cond][speed_cond]
speed_vals = speed[speed_cond]

twinx = ax.twinx()
twinx.plot(speed_range, speed_vals, color="red")
 
# ax[1].plot(t1[:num_coeffs], correlation_coeffs)
