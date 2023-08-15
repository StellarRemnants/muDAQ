#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 09:53:04 2023

@author: stellarremnants
"""

from live_plotter_functions import (
    connect_to_client,
    connect_client_sftp,
    file_open_for_read,
    load_preamble,
    initial_file_load,
    formatter_fnc,
    live_plot_setup,
    live_plotter_loop,
    close_connection,
    )

import json
import argparse
    
# %%
if __name__ == "__main__":

    
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file_path", nargs="?", default="live_plotter_settings.json")
    parser.add_argument("-v", "--verbose", dest="verbose", default=1, action="count")
    parser.add_argument("-s", "--silent", dest="silent", default=False, action="store_true")
    # host = "hephaestus.remote"
    # username = "stellarremnants"
    # file_path = ("muDAQ/analysis_code/thermistor_data/"
    #               "multi_device_example/mde__00011.csv")
    # refresh_period = 0.1
    # plot_last_points = 600
    # margins = [0,0.10]
    # skip_bulk = True
    # init_seek = 1000
    # res = [1200, 800]
    # anchor = (1.15, 0.95)
    
    # args = parser.parse_args()
    args = parser.parse_args(
        
        )
    
    json_file_path = args.json_file_path
    verbose = args.verbose
    silent = args.silent
    
    if silent:
        verbose = 0
    
    with open(json_file_path, "r") as json_fdin:
        json_dict = json.load(json_fdin)
    
    # required_keys = {
    #     "host":None,
    #     "username":None,
    #     "file_path":None,
    #     "refresh_period":None,
    #     "plot_last_points":None,
    #     "margins":None,
    #     "skip_bulk":None,
    #     "init_seek":None,
    #     "res":None,
    #     "anchor":None,
    #     }
    
    # def check_fnc(json_dict, key):
    #     if not (key in json_dict.keys()):
    #         return False
    #     else:
    #         return True
        
    # def recursive_dive(json_dict, key_list):
    #     if len(key_list) == 1:
    #         if check_fnc(json_dict, key_list[0]):
    #             return True
    #         else:
    #             raise KeyError("Missing required key '{key_list[0]}'")
    #     else:
    #         if check_fnc(json_dict, key_list[0]):
    #             if type(json_dict[key_list[0]]) is dict:
    #                 return recursive_dive(json_dict[key_list[0]], key_list[1:])
    #             else:
    #                 raise KeyError(f"Required intermediate key {key_list[0]} "
    #                                "expects entry to be a dictionary, "
    #                                f"is instead of type '{type(json_dict[key_list[0]])}'" )
    #         else:
    #             raise KeyError(f"Could not find intermediate key '{key_list[0]}'")
# %%
    if verbose >= 1:
        print("Connecting to client")
    client = connect_to_client(
        json_dict["Connection Settings"]["host"], 
        json_dict["Connection Settings"]["username"]
        )
    sftp = connect_client_sftp(client)
    fdin = file_open_for_read(
        sftp, 
        json_dict["File Settings"]["file_path"]
        )
    
    fdin, start_datetime, program_dict = load_preamble(fdin)
    
    max_voltage = program_dict["device_list"][0]["max_voltage"]
    bit_resolution = program_dict["device_list"][0]["bit_resolution"]
    
    start_time = start_datetime.timestamp()
    
    columns, channels, data_dict, program_dict = \
        initial_file_load(
            fdin, 
            json_dict["File Settings"]["skip_data_bulk"], 
            json_dict["File Settings"]["initial_read"], 
            json_dict["Plot Settings"]["point_count_per_channel"], 
            program_dict,
            json_dict["File Settings"]["file_path"]
                          )
        
    formatter = formatter_fnc()
    
    fig, ax, lines = live_plot_setup(
            formatter, 
            channels, 
            data_dict, 
            program_dict, 
            json_dict["Plot Settings"]["legend_anchor"], 
            json_dict["Plot Settings"]["data_margins"],
            json_dict["Plot Settings"]["resolution"],
            json_dict["Connection Settings"]["username"],
            json_dict["Connection Settings"]["host"],
            json_dict["File Settings"]["file_path"],
            start_time,
            json_dict["Plot Settings"]["box_width"],
            json_dict["Plot Settings"]["box_height"],
            )
    
    live_plotter_loop(
            fdin, 
            columns, 
            channels, 
            data_dict, 
            json_dict["Plot Settings"]["point_count_per_channel"],
            lines,
            ax,
            program_dict,
            json_dict["Plot Settings"]["legend_anchor"],
            json_dict["Plot Settings"]["data_margins"],
            json_dict["Plot Settings"]["refresh_interval"],
            fig,
            start_time
            )
    
    close_connection(client, sftp)
    