#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 14:28:55 2022

@author: stellarremnants
"""

PIN_DICT = {
    
    "A1":14,
    "A2":15,
    "A3":16,
    "A4":17,
    "A5":18,
    "A6":19,
    
    "A11":11,
    "A12":12,
    "A13":13,
    "A16":16,
    "A29":29,
    "A31":31,
    "A32":32,
    "A33":33,
    "A34":34,
    "A35":35,
    
    }

def validate_pin(pin_str):
    if pin_str in PIN_DICT.keys():
        return True
    else:
        return False
    
def get_pin_id_num(pin_id):
    if type(pin_id) is str:
        valid_pin = validate_pin(pin_id)
        if valid_pin:
            return PIN_DICT[pin_id]
        else:
            raise ValueError(f"Unable to find pin number corresponding to \"{pin_id}\"")
    else:
        return pin_id