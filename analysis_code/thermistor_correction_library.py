#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 18 12:42:50 2022

@author: stellarremnants
"""
import numpy as np

correction_dict = {
    "00": [-1.20823075e+02, 8.18369617e-01, 3.53057987e-05],
    "01": [ 5.41746562e+01, 6.97710223e-01, 4.76483546e-05],
    }

def polynomial_variable(x, *args):
    ret = np.zeros_like(x)
    if ret.size == 1:
        ret = 0.
    for i in range(len(args)):
        ret += args[i] * x**i
    return ret

def correct_resistance(R, sensor_id):
    if not(sensor_id in correction_dict.keys()):
        raise ValueError(f"sensor_id \"{sensor_id}\" not found in correction_dict")
    else:
        return polynomial_variable(R, *correction_dict[sensor_id])