#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  6 08:33:21 2022

@author: stellarremnants
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal

NUM = 10000
xmin = -40
xmax = 40
x = np.linspace(xmin, xmax, num=NUM)
DT = (xmax-xmin)/(NUM-1)

noise_1_amplitude = 0
noise_2_amplitude = 0

def zero_center_noise(noise_amp, size=NUM):
    return (np.random.random(size=size)-0.5)*2 * noise_amp

def y_fnc_sin(x, shift, noise_amp):
    return np.sin(2 * np.pi * (x + shift)) + zero_center_noise(noise_amp)

AMP_1 = 4; AMP_2 = 0; PERIOD_1 = 3; PERIOD_2 = 1;
SLOPE = 0; INTERCEPT = 0;
def y_fnc_sin_2(x, shift, noise_amp):
    signal_1 = AMP_1 * np.sin(2 * np.pi * (x + shift)/PERIOD_1) + zero_center_noise(noise_amp)
    signal_2 = AMP_2 * np.sin(2 * np.pi * (x + shift)/PERIOD_2) + zero_center_noise(noise_amp)
    return signal_1 + signal_2

def y_fnc_sin_3(x, shift, noise_amp):
    signal_1 = AMP_1 * np.sin(2 * np.pi * (x + shift)/PERIOD_1) + zero_center_noise(noise_amp)
    signal_2 = AMP_2 * np.sin(2 * np.pi * (x + shift)/PERIOD_2) + zero_center_noise(noise_amp)
    signal_3 = SLOPE * (x+shift) + INTERCEPT + zero_center_noise(noise_amp)
    return signal_1 + signal_2 + signal_3

def y_fnc_line(x, shift, noise_amp):
    return (x+shift) * SLOPE + INTERCEPT + zero_center_noise(noise_amp)

PARAB_A = 1; PARAB_B = 0; PARAB_C = 0;
def y_fnc_parabola(x, shift, noise_amp):
    return PARAB_A * (x+shift)**2 + PARAB_B * (x+shift) + PARAB_C + zero_center_noise(noise_amp)

def y_fnc_sin_shift(x, shift, noise_amp):
    shift_min = 0
    shift_max = abs(shift)
    shift_array = np.linspace(shift_min, shift_max, x.size)
    signal_1 = AMP_1 * np.sin(2 * np.pi * (x + shift_array)/PERIOD_1) + zero_center_noise(noise_amp)
    return signal_1

def y_fnc_sin_step(x, shift, noise_amp):
    shift_1 = -shift
    shift_2 = shift
    
    x_half = int(x.size//2)
    y = np.zeros_like(x)
    y[0:x_half] = AMP_1 * np.sin( 2 * np.pi * (x[0:x_half] + shift_1) / PERIOD_1 )
    y[x_half:] = AMP_1 * np.sin( 2 * np.pi * (x[x_half:] + shift_2) / PERIOD_1 ) 
    y += zero_center_noise(noise_amp)
    return y

shift_1 = 0
# shift_2 = zero_center_noise(1, size=1)[0]
shift_2 = 0.5

y_fnc = y_fnc_sin_step


y1 = y_fnc(x, shift_1, noise_1_amplitude)
y2 = y_fnc(x, shift_2, noise_2_amplitude)


ones_array = np.ones(NUM)
in_shift = (shift_2-shift_1)
in_shift_x = ones_array * in_shift


def normalize_array(inarray):
    array_min = inarray.min()
    array_max = inarray.max()
    array_span = array_max - array_min
    if array_span > 0:
        return (inarray - array_min) / array_span
    else:
        return inarray


# # %%

# # =============================================================================
# # Classic Correlation Approach
# # =============================================================================
# fig,(ax1, ax2) = plt.subplots(nrows=2, ncols=1)

# ax1.plot(x, y1, label="Signal 1")
# ax1.plot(x, y2, label="Signal 2")
# ax1.legend()

# correlation_array = np.correlate(y1, y2, mode="full")

# max_correlation_arg = np.argmax(correlation_array)
# correlation_arg_shift = max_correlation_arg - correlation_array.size/2
# out_shift = correlation_arg_shift * DT

# correlation_time_args = np.arange(0, correlation_array.size) - correlation_array.size/2
# correlation_times_old = correlation_time_args * DT

# out_shift_x = ones_array * out_shift
# shift_y = np.linspace(correlation_array.min(), correlation_array.max(), NUM)

# ax2.plot(correlation_times_old, correlation_array, marker=".",
#           color="blue", label="Correlation_Coeffs")
# ax2.plot(out_shift_x, shift_y, marker="", color="red",
#           label=f"Max Coeff ({out_shift:.3f})")
# ax2.plot(in_shift_x, shift_y, marker="", color="black",
#           label=f"Input Shift ({in_shift:.3f})")
# ax2.legend()
# fig.suptitle("Sole Correlation Method")


# %%

window_radius = NUM//4
window_size = window_radius*2


search_time_min = -0.75
search_arg_min = search_time_min / DT
search_time_max = 0.75
search_arg_max = search_time_max / DT

center = NUM//2
min_peak_spacing_time = 0.5
arg_start = center-window_radius
arg_end = center+window_radius
signal_1_cut = y1[center-window_radius:center+window_radius]
signal_2_range = np.arange(0, NUM-window_size)
signal_2_delta = arg_start - signal_2_range
signal_2_range = signal_2_range[np.logical_and(
    signal_2_delta <= search_arg_max,
    signal_2_delta >= search_arg_min
    )]
num_coeffs = signal_2_range.size
correlation_coeffs = np.zeros(num_coeffs, dtype=float)

signal_1_adj = signal_1_cut - signal_1_cut.mean()

for i in range(num_coeffs):
    left_2 = signal_2_range[i]
    signal_2_cut = y2[left_2:left_2+window_size]
    signal_2_cut = signal_2_cut - signal_2_cut.mean()
    corr = np.correlate(signal_1_cut, signal_2_cut)
    correlation_coeffs[i] = corr
    
    
correlation_times = (arg_start - signal_2_range) * DT

shift_y = np.linspace(correlation_coeffs.min(), correlation_coeffs.max(), NUM)
    
fig,(ax1, ax2) = plt.subplots(nrows=2, ncols=1)
x_start = x[arg_start]
x_end = x[arg_end]
signal_y = np.linspace(y1.min(), y1.max(), NUM)
signal_x = np.ones_like(signal_y)

ax1.plot(x, y1, label="Signal 1")
ax1.plot(x, y2, label="Signal 2")
ax1.plot(signal_x*x_start, signal_y, color="black")
ax1.plot(signal_x*x_end, signal_y, color="black")
ax1.legend()

ax2.plot(correlation_times, correlation_coeffs, marker=".",
          color="blue", label="Corr New")

min_peak_spacing_arg = min_peak_spacing_time / DT
peaks, peak_porperties = signal.find_peaks(abs(correlation_coeffs), distance=min_peak_spacing_arg)
anti_peaks, anti_peak_porperties = signal.find_peaks(-correlation_coeffs, distance=min_peak_spacing_arg)
np.concatenate([peaks, anti_peaks])
for peak_arg in peaks:
    peak_time = correlation_times[peak_arg]
    peak_val = correlation_coeffs[peak_arg]
    ax2.plot(peak_time, peak_val, color="red", marker="x",
              label=f"Peak: {peak_time:.3f}")
    ax2.plot(peak_time * ones_array, shift_y, color="red")
ax2.plot(in_shift_x, shift_y, marker="", color="black",
          label=f"Input Shift ({in_shift:.3f})")
ax2.legend()
fig.suptitle("Window Method")

# %%
# def windowed_delay_correlation(signal_1, signal_2,
#                                window_size = None,
#                                )
signal_1 = y1
signal_2 = y2
num_1 = signal_1.size
num_2 = signal_2.size
min_num = np.min([num_1, num_2])
# window_size = min_num//8
window_size = 500

search_time_min = -2
search_time_max = 2
search_arg_min = search_time_min / DT
search_arg_max = search_time_max / DT

num_1_range = np.arange(0, num_1-window_size)
num_2_range = np.arange(0, num_2-window_size)

rmax_1 = num_1_range.size
rmax_2 = num_2_range.size

correlation_coefficients = np.zeros([rmax_1, rmax_2], dtype=float)

dplaces_1 = int(np.ceil(np.log10(rmax_1)))

for start_1 in num_1_range:
    print(f"\rSingal 1 ({start_1+1:0{dplaces_1}d}/{rmax_1})", end="")
    check_min = np.max([0, start_1 + search_arg_min])
    check_max = np.min([rmax_2, start_1 + search_arg_max])
    check_range = num_2_range[np.logical_and(
        num_2_range >= check_min,
        num_2_range <= check_max
        )]
    sig1 = signal_1[start_1:start_1+window_size]
    sig1 = sig1-sig1.mean()
    for start_2 in check_range:
        sig2 = signal_2[start_2:start_2+window_size]
        sig2 = sig2-sig2.mean()
        corr = np.correlate(sig1, sig2)
        correlation_coefficients[start_1, start_2] = corr
# %%
delay_args = np.zeros(rmax_1, dtype = float)
slice_x = np.arange(0, rmax_2)
search_width = int((search_arg_max - search_arg_min)/4)
peak_distance = search_width
fig,ax=plt.subplots()

peak_array = np.zeros_like(delay_args)

compare_len = 10
plot_count = 10
plot_every = rmax_1 // plot_count

for start_1 in num_1_range:
    
    
    check_min = np.max([0, start_1 + search_arg_min])
    check_max = np.min([rmax_2, start_1 + search_arg_max])
    check_range = num_2_range[np.logical_and(
        num_2_range >= check_min,
        num_2_range <= check_max
        )]
    
    slice_y = correlation_coefficients[start_1, check_range]
    max_arg = np.argmax(slice_y) 
    peaks, peak_properties = signal.find_peaks(slice_y, distance = peak_distance)
    # peaks = []
    if len(peaks) == 0:
        peak_arg = max_arg
    else:
        if start_1 > compare_len:
            offset = np.mean(peak_array[start_1-compare_len:start_1])
        else:
            offset = slice_y.min()
        # peak_arg = peaks[np.argmin(abs( (peaks-offset) / slice_y[peaks]))]
        peak_arg = max_arg
    # norm_y = (slice_y - slice_y.min())/(slice_y.max()-slice_y.min()) 
    # max_arg = np.sum(slice_x * norm_y**2)/np.sum(norm_y**2)
    peak_array[start_1] = peak_arg
    delay_args[start_1] = start_1 - check_range[peak_arg]
    
    if start_1 % plot_every == 0:
        ax.plot(check_range, slice_y)
        ax.plot(check_range[peak_arg], slice_y[peak_arg], marker="x", color="red")
    
delay_times = delay_args * DT
mean_delay = np.mean(delay_times[search_width:-search_width])
mean_arg = np.mean(delay_args[search_width:-search_width])
fig.suptitle("Peak Sensing Quality Check")

# %%
fig,(ax1d, ax2d)=plt.subplots(nrows=1, ncols=2)
fig.set_size_inches(np.asarray([1920,1080])/fig.dpi)
ax2d.imshow(correlation_coefficients.T,
          origin="lower",
          interpolation="None")

# for start_1 in num_1_range:
ax2d.plot(num_1_range[search_width:-search_width], 
          (num_1_range - delay_args)[search_width:-search_width],
          color="red", marker=".", label="Maxima")
ax2d.plot(num_1_range, num_1_range, color="cyan", label="0 delay")
ax2d.plot(num_1_range+ mean_arg, num_1_range , color="orange", label=f"Mean Delay {mean_delay:.3f}")
ax2d.plot(num_1_range+ shift_2/DT, num_1_range , color="black", label=f"Input Delay {shift_2:.3f}")
ax2d.legend()

ax1d.set_xlabel("Signal 1 Index")
ax1d.set_ylabel("Signal 2 Index")


ax1d.plot(num_1_range[search_width:-search_width], 
          delay_times[search_width:-search_width],
          label="Delay Times")
ax1d.plot(num_1_range, np.ones_like(num_1_range)*mean_delay, color="orange", 
          label=f"Mean Delay {mean_delay:.3f}")
ax1d.plot(num_1_range, np.ones_like(num_1_range)*shift_2, color="black", 
          label=f"Input Delay {shift_2:.3f}")
ax1d.legend()

ax1d.set_xlabel("Signal 1 Index")
ax1d.set_ylabel("Delay")
fig.suptitle("Time Series Window Results")

# %%
# fig, ax = plt.subplots()

# indices = np.arange(0, rmax_1, step=int(num_1//10))
# for i in indices:
#     check_min = int(np.max([0, i + search_arg_min]))
#     check_max = int(np.min([rmax_2, i + search_arg_max]))
#     check_range = num_2_range[np.logical_and(
#         num_2_range >= check_min,
#         num_2_range <= check_max
#         )]
    
#     corr_data = correlation_coefficients[i, check_range]
#     ax.plot(check_range, corr_data)
    
#     ax.plot(i - int(delay_args[i]), 
#             correlation_coefficients[i, i-int(delay_args[i])], 
#             color="red", marker="x")
# fig.suptitle("Time Series Window Post-Check")

# # %%
# fig, ax = plt.subplots()
# slice_arg = 1500
# slice_y = correlation_coefficients[slice_arg,:]
# slice_x = np.arange(slice_y.size)
# norm_y = (slice_y - slice_y.min())/(slice_y.max()-slice_y.min()) 

# weighted_mean = np.sum(slice_x*norm_y)/np.sum(norm_y)
# sq_mean = np.sum(slice_x * norm_y**2)/np.sum(norm_y**2)

# ones_y = np.linspace(norm_y.min(), norm_y.max(), 100)
# ones_x = np.ones_like(ones_y)

# ax.plot(slice_x, norm_y)
# ax.plot(ones_x*weighted_mean, ones_y)
# ax.plot(ones_x*sq_mean, ones_y)