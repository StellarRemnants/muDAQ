#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 11:23:27 2023

@author: stellarremnants
"""

import numpy as np
import matplotlib.pyplot as plt

def random_data_generator(*array_size):
    return np.random.rand(*array_size)

def create_figure(
        ylim=None,
        xlim=None,
        ):
    fig, ax = plt.subplots()
    if not (ylim is None):
        ax.set_ylim(ylim)
    if not (xlim is None):
        ax.set_xlim(xlim)
        
    return fig, ax

def smart_append(orig_data, new_data):
    
    if not(orig_data.shape[1:] == new_data.shape):
        if not(len(orig_data.shape) == len(new_data.shape)):
            pass # Cannot be coerced
        else:
            if not(orig_data.shape[1:] == new_data.shape[1:]):
                pass # cannot be coerced
            else:
                return np.append(orig_data, new_data, axis=0) # append along axis 0
    else:
        return np.append(orig_data, [new_data], axis=0) # append along axis 0 using list wrap around new_data
    
    
def smart_queue_rotate(orig_data, new_data, max_length=None):
    if max_length is None:
        max_length = orig_data.shape[0]
        
    appended_data = smart_append(orig_data, new_data)
    new_length = appended_data.shape[0]
    return appended_data[new_length-max_length:]

if __name__ == "__main__":
    fig, ax = create_figure()
    
    data_shape = [20, 2]
    x_vals = np.arange(0, data_shape[0])
    data = random_data_generator(*data_shape)
    line_list = []
    for i in range(data_shape[1]):
        line_list.append(ax.plot(x_vals, data[:,i]))
    