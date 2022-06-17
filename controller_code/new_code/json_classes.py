#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 25 08:25:14 2022

@author: stellarremnants
"""

import json
import os

from global_constants import INIT_BAUD, SERIAL_READ_TIMEOUT

DEFAULT_IGNORE_FIRST_LINES = 10
DEFAULT_CHECK_PORT_EXISTS = False
DEFAULT_COLLECTION_MODE = "duration"
DEFAULT_COLLECTION_DURATION = 10
DEFAULT_COLLECTION_COUNT = 1000

# =============================================================================
# Functions
# =============================================================================
def is_string(test_str):
    if type(test_str) is str:
        return test_str
    else:
        raise ValueError(f"Input is not a string: {test_str}")
    
def list_of_type(test_list, test_type):
    
    if len(test_list) == 0:
        raise ValueError(f"Invalid {test_type} list: Empty list.")
    else:
        for i in range(len(test_list)):
            item = test_list[i]
            if not(isinstance(item, test_type)):
                raise ValueError(f"Invalid {test_type} list: List index {i} "
                                 f"is of type {type(item)}.")
        
        return test_list

# =============================================================================
# channel_settings
# =============================================================================
class channel_settings:
    
    def __repr__(self):
        return f"Channel Settings Instance: {self.__str__()}"
    
    def __str__(self):
        return self.to_json()
    
    def to_dict(self):
        return self.__dict__
    
    def from_dict(indict):
        required_keys = [
            "channel_name",
            "pin_id",
            "pin_delay",
            "sensor_type",
            "ref_resistance",
            "ref_voltage",
            ]
        
        optional_keys = [
            ]
        for key in indict.keys():
            if not (key in required_keys) and not (key in optional_keys):
                raise ValueError(
                    f"Unknown program_settings key: {key}"
                    )
        for key in required_keys:
            if not key in indict.keys():
                raise ValueError(
                    f"Missing required program_settings key: {key}"
                    )
        
        req_args = {}
        for req_key in required_keys:
            req_args[req_key] = indict[req_key]
        
        opt_args = {}
        for opt_key in optional_keys:
            if opt_key in indict.keys():
                opt_args[opt_key] = indict[opt_key]
                
        pass_args = {}
        for req_key in req_args.keys():
            pass_args[req_key] = req_args[req_key]
        for opt_key in opt_args.keys():
            if not opt_key in pass_args.keys():
                pass_args[opt_key] = opt_args[opt_key]
            else:
                raise ValueError(f"Got repeated definition of optional key {opt_key}")
                
        return channel_settings(**pass_args)
    
    def to_json(self, *args, **kwargs):
        return json.dumps(self, *args, default=lambda o: o.__dict__, **kwargs)
    
    def __init__(
            self,
            channel_name,
            pin_id,
            pin_delay,
            sensor_type = "thermistor",
            ref_resistance = 10000,
            ref_voltage = 3.3,
            ):
        self.channel_name = self.validate_name(channel_name)
        self.pin_id = pin_id
        self.pin_delay = pin_delay
        self.sensor_type = sensor_type
        self.ref_resistance = ref_resistance
        self.ref_voltage = ref_voltage
        
    
    def validate_name(
            self,
            name,
            ):
        return is_string(name)

# =============================================================================
# device_settings
# =============================================================================
class device_settings:
    
    def __repr__(self):
        return f"Device Settings Instance: {self.__str__()}"
    
    def __str__(self):
        return self.to_json()
    
    def to_dict(self):
        return self.__dict__
    
    def from_dict(indict):
        required_keys = [
            "device_name",
            "channel_list",
            "port",
            "data_file_prefix",
            ]
        
        optional_keys = [
            "baudrate",
            "ignore_first_lines",
            "check_port_exists",
            "collection_mode",
            "collection_duration",
            "collection_count",
            "delay_on_empty",
            "max_voltage",
            "bit_resolution",
            ]
        for key in indict.keys():
            if not (key in required_keys) and not (key in optional_keys):
                raise ValueError(
                    f"Unknown program_settings key: {key}"
                    )
        for key in required_keys:
            if not key in indict.keys():
                raise ValueError(
                    f"Missing required program_settings key: {key}"
                    )
        
        req_args = {}
        for req_key in required_keys:
            req_args[req_key] = indict[req_key]
        
        opt_args = {}
        for opt_key in optional_keys:
            if opt_key in indict.keys():
                opt_args[opt_key] = indict[opt_key]
                
        channel_list = req_args["channel_list"]
        if not(len(channel_list)):
            raise ValueError("Input channel_list is empty. Cannot create program_settings")
        else:
            for i in range(len(channel_list)):
                if not isinstance(channel_list[i], channel_settings):
                    if type(channel_list[i]) is dict:
                        channel_list[i] = channel_settings.from_dict(channel_list[i])
                    else:
                        raise ValueError(
                            f"Unable to cast item of type {type(channel_list)} to"
                            f" type {channel_settings}."
                            )
        req_args["channel_list"] = channel_list
        
        pass_args = {}
        for req_key in req_args.keys():
            pass_args[req_key] = req_args[req_key]
        for opt_key in opt_args.keys():
            if not opt_key in pass_args.keys():
                pass_args[opt_key] = opt_args[opt_key]
            else:
                raise ValueError(f"Got repeated definition of optional key {opt_key}")
                
        return device_settings(**pass_args)
    
    def to_json(self, *args, **kwargs):
        return json.dumps(self, *args, default=lambda o: o.__dict__, **kwargs)
    
    def __init__(
            self,
            device_name,
            channel_list,
            port,
            data_file_prefix,
            baudrate = INIT_BAUD,
            ignore_first_lines = DEFAULT_IGNORE_FIRST_LINES,
            check_port_exists = False,
            collection_mode = DEFAULT_COLLECTION_MODE,
            collection_duration = 10,
            collection_count = None,
            delay_on_empty = 0.01,
            max_voltage = 2,
            bit_resolution = 14,
            ):
        
        if os.path.exists(port) or not check_port_exists:
            self.port = port
        else:
            raise ValueError(f"Invalid device port \"{port}\". Does not Exist!")
        
        self.device_name = self.validate_name(device_name)
        self.data_file_prefix = data_file_prefix
        self.baudrate = baudrate
        self.ignore_first_lines = ignore_first_lines
        self.check_port_exists = check_port_exists
        self.collection_mode = collection_mode
        self.collection_duration = collection_duration
        self.collection_count = collection_count
        self.delay_on_empty = delay_on_empty
        self.max_voltage = max_voltage
        self.bit_resolution = bit_resolution
        self.channel_list = self.validate_channel_list(channel_list)
        
        
    def validate_name(
            self,
            name
            ):
        return is_string(name)
    
    def validate_channel_list(
            self,
            channel_list
            ):
        ch_list = list_of_type(channel_list, channel_settings)
        
        channel_names = []
        for ch in ch_list:
            if ch.channel_name in channel_names:
                raise ValueError(
                    f"Repeated channel name \"{ch.channel_name}\" under device"
                    f" \"{self.device_name}\". Channel names must be unique."
                    )
            else:
                channel_names.append(ch.channel_name)
        
        return ch_list
        
# =============================================================================
# program_settings
# =============================================================================
class program_settings:
    
    def __repr__(self):
        return f"Program Settings Instance: {self.__str__()}"
    
    def __str__(self):
        return self.to_json()
    
    def to_dict(self):
        return self.__dict__
    
    def from_dict(indict):
        required_keys = [
            'program_name', 
            'delay_on_empty', 
            'device_list'
            ]
        
        optional_keys = [
            "baudrate",
            "ignore_first_lines",
            "check_port_exists",
            ]
        
        for key in indict.keys():
            if not (key in required_keys) and not (key in optional_keys):
                raise ValueError(
                    f"Unknown program_settings key: {key}"
                    )
        for key in required_keys:
            if not key in indict.keys():
                raise ValueError(
                    f"Missing required program_settings key: {key}"
                    )
        
        req_args = {}
        for req_key in required_keys:
            req_args[req_key] = indict[req_key]
        
        opt_args = {}
        for opt_key in optional_keys:
            if opt_key in indict.keys():
                opt_args[opt_key] = indict[opt_key]
                
        device_list = req_args["device_list"]
        
        if not (len(device_list)):
            raise ValueError("Input device_list is empty. Cannot create program_settings")
        else:
            for i in range(len(device_list)):
                if not isinstance(device_list[i], device_settings):
                    if type(device_list[i]) is dict:
                        device_list[i] = device_settings.from_dict(device_list[i])
        
        req_args["device_list"] = device_list     
        
        
        pass_args = {}
        for req_key in req_args.keys():
            pass_args[req_key] = req_args[req_key]
        for opt_key in opt_args.keys():
            if not opt_key in pass_args.keys():
                pass_args[opt_key] = opt_args[opt_key]
            else:
                raise ValueError(f"Got repeated definition of optional key {opt_key}")
            
        return program_settings(**pass_args)
    
    def to_json(self, *args, **kwargs):
        return json.dumps(self, *args, default=lambda o: o.__dict__, **kwargs)
    
    def __init__(
            self,
            program_name,
            device_list,
            delay_on_empty = SERIAL_READ_TIMEOUT,
            ):
        
        self.program_name = self.validate_name(program_name)
        self.delay_on_empty = delay_on_empty
        self.device_list = self.validate_device_list(device_list)
        
    def validate_name(
            self,
            name
            ):
        return is_string(name)
    
    def validate_device_list(
            self,
            device_list,
            ):
        return list_of_type(device_list, device_settings)
    
    
# %%
if __name__ == "__main__":
    channel_indices = [29, 11, 34]
    ch_list = [channel_settings(f"CH{i:01d}", channel_indices[i], 500) for i in range(3)]
    dev = device_settings(
    "Arduino Artemis ATP - Flow Sensors", 
    ch_list, 
    "/dev/ttyUSB0",
    "data/test_file",
    check_port_exists = False
    )
    pr = program_settings("Template", [dev], delay_on_empty=0.01)
    
    pr2 = program_settings.from_dict(json.loads(pr.to_json()))
    
    print("=======Original======")
    print(pr.to_json(indent=2))
    print()
    print("=======Reloaded======")
    print(pr2.to_json(indent=2))
    print()
    print("=======Match?======")
    print(pr2.to_json() == pr.to_json())
    
    with open(f"{pr.program_name}.json", "w") as fdout:
        fdout.write(pr.to_json(indent=2))