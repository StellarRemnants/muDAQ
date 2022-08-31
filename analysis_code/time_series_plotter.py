#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 15:05:32 2022

@author: stellarremnants
"""

from file_read_functions import process_data_from_path
import matplotlib.pyplot as plt
import numpy as np
# import sys
import argparse

# from scipy.signal import savgol_filter

MAX_TIME = 2**32
DEFAULT_BIN_TIME = 5 #s

DEFAULT_FILE_PATH = ("/home/stellarremnants/muDAQ/analysis_code/"
                     "thermistor_data/multi_device_test/mdt__0015.csv")

if __name__ == "__main__":
    
    
    
    plt.ion()
    
    parser = argparse.ArgumentParser(
        description="Time Series Plotter for muDAQ formatted .csv data files.",
        prog="muDAQ Time Series Plotter",
        )
    # argv = sys.argv
    # # print(argv)
    # if len(argv) < 2:
    #     file_path = DEFAULT_FILE_PATH
    # elif len(argv) > 2:
    #     raise ValueError("Too many inputs. Expected exactly 1 path as input.")
    # else:
    #     file_path = argv[1]
    parser.add_argument("file_path", type=str, nargs="?", action="store",
                        default=DEFAULT_FILE_PATH,
                        help=(f"Path to the .csv file containing muDAQ formatted data. "
                              f"Default={DEFAULT_FILE_PATH}"))
    
    parser.add_argument("--bin_time", type=float, action="store",
                        dest="bin_time", default=DEFAULT_BIN_TIME,
                        help=(f"Length of bins to use when time averaging the data. Use a value of 0 to not use bins."
                              f"Default={DEFAULT_BIN_TIME:.2f}s")
                        )
    
    
    
    args = parser.parse_args()
        
    file_path = args.file_path
    bin_time = args.bin_time
    
    print(f"file_path={file_path}")
    print(f"bin_time={bin_time:.2f}")
        
    print(f"Loading file: {file_path}")
    
    all_device_dict, program_dict, start_datetime = process_data_from_path(file_path, 
                                                                 correct_on_sensor_id=True,
                                                                 correct_R_to_T_directly=True)
    for dev_id in all_device_dict.keys():
        data_dict = all_device_dict[dev_id]
        dev_opts = program_dict["device_list"][dev_id]
        channel_names = {}
        for pin_id in data_dict.keys():
            matches = []
            for ch_dict in dev_opts["channel_list"]:
                if ch_dict['pin_id'] == pin_id:
                    matches.append(ch_dict["channel_name"])
                    
            if len(matches) < 1:
                print(f"No matches found for channel {pin_id}")
            elif len(matches) > 1:
                print(f"Multiple matches found for channel {pin_id}")
                
            else:
                channel_names[pin_id] = matches[0]
                
                
        pin_ids = list(channel_names.keys())
        NUM_PINS = len(pin_ids)
        
    # %%
        
        compressed_dict = {}
        init_time = np.min([np.min(data_dict[ch_id]["TIME"][:10]) for ch_id in pin_ids]) * 1e-6
        
        
        # channel_ids = np.asarray([channel_names[ch_id] for ch_id in pin_ids])
        channel_ids_list = np.asarray([(ch_id, channel_names[ch_id]) for ch_id in pin_ids], 
                                      dtype=object)
        channel_ids_list = channel_ids_list[channel_ids_list[:,1].argsort()]
        print()
        print(f"Binning time series data with bin size: {bin_time:.2f}s")
        print()
        
        for i in range(NUM_PINS):
            print(f"Channel: {i+1}/{NUM_PINS}")
            ch_id, channel_name = channel_ids_list[i]
            dataframe = data_dict[ch_id]
            time = dataframe["TIME"] * 1e-6 - init_time
            temp = dataframe["temp_C"]
            
            rollover_cond = np.asarray([False, *(np.diff(time) < -10)])
            for j in np.arange(time.size)[rollover_cond]:
                time[j:] += MAX_TIME*1e-6
                
            if bin_time > 0:
                
                mean_dt = np.mean(np.diff(time))
                counts, bins = np.histogram(time, bins=int(np.ceil((time.iloc[-1]-time.iloc[0])/bin_time)))
                compressed_size = counts.size
                compressed_times = (bins[:-1]+bins[1:])/2
                compressed_temps = np.zeros(compressed_size)
                compressed_temp_errors = np.zeros(compressed_size)
                
                for j in range(compressed_size):
                    print(f"\r  BIN: {j+1}/{compressed_size} ({(j+1)/compressed_size:03.1%})", end="")
                    condition = np.logical_and(time >= bins[j], time < bins[j+1])
                    compressed_temps[j] = np.mean(temp[condition])
                    compressed_temp_errors[j] = np.std(temp[condition])/(counts[j]**0.5)
                print()
                print()
            
            else:
                compressed_times = time
                compressed_temps = temp
                compressed_temp_errors = np.zeros_like(compressed_times)
            
            compressed_dict[ch_id] = (compressed_times, compressed_temps, compressed_temp_errors)
        
        
        
        
        
        # %%
        # fig, axes = plt.subplots(nrows=NUM_PINS, sharex=True)
        fig, axes = plt.subplots(nrows=1, sharex=True)
        axes = list([axes])
        
        print("Plotting Time Series")
        for i in range(NUM_PINS):
            # print(f"PIN: {i+1}/{NUM_PINS}")
            ch_id, channel_name = channel_ids_list[i]
            
            time, temp, temp_error = compressed_dict[ch_id]
            
            if bin_time > 0:
                axes[0].errorbar(time, temp, yerr=temp_error, label=f"CH:{ch_id:02d} :: {channel_name}",
                                  ls="-", marker=".", capsize=2,
                                  )
            else:
                axes[0].plot(time, temp, label=f"CH:{ch_id:02d} :: {channel_name}",
                                  ls="-", marker=".",
                                  )
        
        axes[0].legend(loc="upper right")
        axes[0].grid()
        axes[0].set_xlabel("Time Elapsed [s]")
        axes[0].set_ylabel(r"Temperature [$^\circ$C]")
        fig.suptitle(f"Time Series: {start_datetime.ctime()}\n{file_path.split('/')[-1]}")
        fig.set_size_inches(np.asarray([1920, 1080])/fig.dpi)
        plt.draw()
        
        # %%
        
        if "Hotspot Right" in channel_ids_list[:,1]:
            fig2, ax2 = plt.subplots()
            
            print("Plotting Temperature Differences")
            
            hotspot_right_index = channel_ids_list[channel_ids_list[:,1] == "Hotspot Right"][0][0]
            hotspot_left_index = channel_ids_list[channel_ids_list[:,1] == "Hotspot Left"][0][0]
            hotspot_middle_index = channel_ids_list[channel_ids_list[:,1] == "Hotspot Middle"][0][0]
            basal_inner_index = channel_ids_list[channel_ids_list[:,1] == "Basal Inner"][0][0]
            basal_outer_index = channel_ids_list[channel_ids_list[:,1] == "Basal Outer"][0][0]
            
            
            hotspot_right_time, hotspot_right_temp, hotspot_right_temp_error = compressed_dict[hotspot_right_index]
            hotspot_left_time, hotspot_left_temp, hotspot_left_temp_error = compressed_dict[hotspot_left_index]
            hotspot_middle_time, hotspot_middle_temp, hotspot_middle_temp_error = compressed_dict[hotspot_middle_index]
            basal_inner_time, basal_inner_temp, basal_inner_temp_error = compressed_dict[basal_inner_index]
            basal_outer_time, basal_outer_temp, basal_outer_temp_error = compressed_dict[basal_outer_index]
            
            min_len = np.min([arr.size for arr in [
                hotspot_right_time,
                hotspot_left_time,
                hotspot_middle_time,
                basal_inner_time,
                basal_outer_time
                ]])
            
            ax2.plot(hotspot_right_time[:min_len], hotspot_left_temp[:min_len]-hotspot_right_temp[:min_len], 
                      label="Hotspot Left-Right", ls="-", marker=".")
            ax2.plot(hotspot_right_time[:min_len], 
                      (hotspot_right_temp[:min_len]+hotspot_left_temp[:min_len])/2-hotspot_middle_temp[:min_len], 
                      label="Hotspot mean(Right & Left) - Middle", ls="-", marker=".")
            
            ax2.legend()
            ax2.grid()
            
            ax2.set_xlabel("Time Elapsed [s]")
            ax2.set_ylabel(r"Temperature Difference [$^\circ$C]")
            fig2.suptitle(f"Time Series Differences: {start_datetime.ctime()}\n{file_path.split('/')[-1]}")
            fig2.set_size_inches(np.asarray([1920, 1080])/fig.dpi)
            
            plt.draw()
            
        # %%
        fig3, ax3 = plt.subplots()
        fig3.set_size_inches(np.asarray([1920,1080])/fig3.dpi)
        for i in range(NUM_PINS):
            ch_id, channel_name = channel_ids_list[i]
            time, temp, error = compressed_dict[ch_id]
            
            cond = np.isfinite(temp)
            if np.any(cond):
                rfft = np.abs(np.real(np.fft.rfft(temp[cond]-np.mean(temp[cond]))))
                psd = rfft**2
                dt = np.mean(np.diff(time))
                freqs = np.fft.rfftfreq(time[cond].size, d=dt)
                
                plot_freqs = freqs[1:]
                plot_period = 1/plot_freqs
                plot_rfft = rfft[1:]
                plot_psd = psd[1:]
                
                fnc = ax3.semilogx
                fnc(plot_period, plot_rfft, ls="-", lw=0.5, marker=".", ms=2)
                
                ax3.set_xlabel("Signal Period [s]")
                ax3.set_ylabel(r"ASD [$\frac{^\circ C}{\sqrt{Hz}}$]")
                ax3.grid()
            
        # %%
        input("Press ENTER to close plots.")