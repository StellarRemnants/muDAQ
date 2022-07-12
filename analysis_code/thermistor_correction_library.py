#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 18 12:42:50 2022

@author: stellarremnants
"""
import numpy as np

CORRECTION_DICT = { # Newest (2022-07-12) calibrations
	"00" : [-4.46984859e+06,  3.59949015e+03, -1.19935851e+00,  2.11842193e-04,
            -2.09159370e-08,  1.09466230e-12, -2.37291127e-17,],
	"01" : [-4.47533585e+06,  3.63686560e+03, -1.22311894e+00,  2.18084040e-04,
            -2.17382861e-08,  1.14868028e-12, -2.51418457e-17],
	"02" : [-2.26935447e+06,  1.86055931e+03, -6.30645775e-01,  1.13295340e-04,
            -1.13713167e-08,  6.04621390e-13, -1.33065373e-17,],
    "03" : [-2.05930931e+06,  1.69099759e+03, -5.74005194e-01,  1.03277020e-04,
            -1.03818410e-08,  5.52879143e-13, -1.21871829e-17,],
    "04" : [-7.40886043e+05,  6.06771676e+02, -2.05070867e-01,  3.67895176e-05,
            -3.68869868e-09,  1.95986198e-13, -4.31100012e-18,],
	}

def polynomial_variable(x, *args):
    ret = np.zeros_like(x)
    if ret.size == 1:
        ret = 0.
    for i in range(len(args)):
        ret += args[i] * x**i
    return ret

def correct_resistance(R, sensor_id):
    if not(sensor_id in CORRECTION_DICT.keys()):
        raise ValueError(f"sensor_id \"{sensor_id}\" not found in correction_dict")
    else:
        return polynomial_variable(R, *CORRECTION_DICT[sensor_id])