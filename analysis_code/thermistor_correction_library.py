#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 18 12:42:50 2022

@author: stellarremnants
"""
import numpy as np

# CORRECTION_DICT = { # Old calibrations (old format)
#     "00": [-1.20823075e+02, 8.18369617e-01, 3.53057987e-05],
#     "01": [ 5.41746562e+01, 6.97710223e-01, 4.76483546e-05],
#     }
# CORRECTION_DICT = { # Old calibrations (reformat)
# 	"00" : [-1.2082e+02,  8.1837e-01,  3.5306e-05, ],
# 	"01" : [ 5.4175e+01,  6.9771e-01,  4.7648e-05, ],
# 	}
CORRECTION_DICT = { # Newest (2022-06-21) calibrations
	"00" : [-9.6672e+01,  9.1816e-01,  1.2244e-05, ],
	"01" : [-3.3676e+01,  9.6349e-01,  1.0955e-05, ],
	"02" : [ 4.4043e+00,  1.1898e+00, -1.4251e-05, ],
    "03" : [0,1,0],
    "04" : [0,1,0],
	}
# CORRECTION_DICT = { # All data - larger errors, potential 
                      #  discrepancies between measurment times
# 	"00" : [-3.1952e+02,  9.8798e-01,  7.4184e-06, ],
# 	"01" : [-1.8292e+02,  9.2676e-01,  1.6822e-05, ],
# 	"02" : [ 4.4043e+00,  1.1898e+00, -1.4251e-05, ],
# 	}

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