#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 18 12:42:50 2022

@author: stellarremnants
"""
import numpy as np

R_TO_R_CORRECTION_DICT = { # Newest (2022-07-12) calibrations
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

R_TO_T_CORRECTION_DICT = {
    
    "00" : [9.7672820e+01, -2.1717580e-02, 2.5245335e-06, -1.1199123e-10, ],
    "01" : [8.8212339e+01, -1.5050860e-02, 1.3450095e-06, -4.7502723e-11, ],
    "02" : [9.0052841e+01, -1.5510218e-02, 1.4249456e-06, -5.2962467e-11, ],
    "03" : [8.9894295e+01, -1.5453540e-02, 1.4180005e-06, -5.2602695e-11, ],
    "04" : [8.9752053e+01, -1.5417217e-02, 1.4156127e-06, -5.2649491e-11, ],
    
    "K01" : [8.1562177e+01, -1.1709842e-02, 8.8705514e-07, -2.8228773e-11, ],
    "K02" : [8.3064877e+01, -1.2347811e-02, 9.9251196e-07, -3.3806238e-11, ],
    "K03" : [8.1368358e+01, -1.1632927e-02, 8.7405804e-07, -2.7587570e-11, ],
    "K04" : [8.1509732e+01, -1.1721573e-02, 8.9335747e-07, -2.8680736e-11, ],
    "K05" : [8.2753583e+01, -1.2398965e-02, 9.9720772e-07, -3.3906566e-11, ],
    "K06" : [8.2168880e+01, -1.2120154e-02, 9.5250109e-07, -3.1655182e-11, ],
    "K07" : [8.1329906e+01, -1.1709664e-02, 8.9037518e-07, -2.8492340e-11, ],
    }

def polynomial_variable(x, *args):
    ret = np.zeros_like(x)
    if ret.size == 1:
        ret = 0.
    for i in range(len(args)):
        ret += args[i] * x**i
    return ret

def correct_resistance_to_resistance(R, sensor_id):
    if not(sensor_id in R_TO_R_CORRECTION_DICT.keys()):
        raise ValueError(f"sensor_id \"{sensor_id}\" not found in correction_dict")
    else:
        return polynomial_variable(R, *R_TO_R_CORRECTION_DICT[sensor_id])
    
def correct_resistance_to_temperature(R, sensor_id):
    if not(sensor_id in R_TO_T_CORRECTION_DICT.keys()):
        raise ValueError(f"sensor_id \"{sensor_id}\" not found in correction_dict")
    else:
        return polynomial_variable(R, *R_TO_T_CORRECTION_DICT[sensor_id])