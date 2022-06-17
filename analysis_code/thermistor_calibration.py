#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 16:39:46 2022

@author: stellarremnants
"""

import pandas
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def ln_fit_variable(R, *args):
    log_R = np.log(R)
    dat = np.zeros_like(log_R)
    
    for i in range(len(args)):
        dat += args[i] * log_R ** i
    return dat
    
MIN_LN = 0
MAX_LN = 7

def ln_fit_fnc_multi(max_pow=3):
    if max_pow > MAX_LN or max_pow < MIN_LN:
        raise ValueError(f"max_pow value {max_pow} is out of allowed range [{MIN_LN}, {MAX_LN}]")
    else:
        if max_pow == 0:
            def fnc(R, a):
                return ln_fit_variable(R, a)
        elif max_pow == 1:
            def fnc(R, a, b):
                return ln_fit_variable(R, a, b)
        elif max_pow == 2:
            def fnc(R, a, b, c):
                return ln_fit_variable(R, a, b, c)
        elif max_pow == 3:
            def fnc(R, a, b, c, d):
                return ln_fit_variable(R, a, b, c, d)
        elif max_pow == 4:
            def fnc(R, a, b, c, d, e):
                return ln_fit_variable(R, a, b, c, d, e)
        elif max_pow == 5:
            def fnc(R, a, b, c, d, e, f):
                return ln_fit_variable(R, a, b, c, d, e, f)
        elif max_pow == 6:
            def fnc(R, a, b, c, d, e, f, g):
                return ln_fit_variable(R, a, b, c, d, e, f, g)
        elif max_pow == 7:
            def fnc(R, a, b, c, d, e, f, g, h):
                return ln_fit_variable(R, a, b, c, d, e, f, g, h)
        
        
        
        return fnc
    
# %%
if __name__ == "__main__":
    
    calibration_data_file = "thermisor_factory_calibration_data.csv"
    
    dataframe = pandas.read_csv(calibration_data_file)
    
    fig, ax = plt.subplots()
    misfit_ax = ax.twinx()
    
    ax.semilogx(dataframe["R"], dataframe["T"], label="Factory Fit Data", color="k")
    
    ax.grid(which="both")
    ax.set_ylabel(r"Temperature [$^\circ$C]")
    ax.set_xlabel(r"Resistance [$\Omega$]")
    
    
    
    # def ln_fit_function(R, a, b, c, d):
    #     log_R = np.log(R)
        
    #     return (a + b * log_R + c * log_R**2 + d * log_R**3)
    
    
    # def ln_fit_function(R, a, b, c, d, e):
    #     log_R = np.log(R)
        
    #     return (a + b * log_R + c * log_R**2 + d * log_R**3 + e * log_R**4)
    
    
    colors = [
        "tab:blue",
        "tab:orange",
        "tab:green",
        "tab:red",
        "tab:purple",
        "cyan",
        "magenta",
        "yellow"
        ]
    
    powers = [3, 4, 5, 6, 7]
    
    edge = 0.0
    
    rest = [int(dataframe["R"].size*edge), int(dataframe["R"].size*(1-edge))]
    fit_fncs = [ln_fit_fnc_multi(p) for p in powers]
    for i in range(len(fit_fncs)):
        fit_fnc = fit_fncs[i]
        ln_fits, ln_errors = curve_fit(fit_fnc, dataframe["R"][rest[0]:rest[1]], dataframe["T"][rest[0]:rest[1]])
        ln_new_T = fit_fnc(dataframe["R"], *ln_fits)
        ln_misfit = dataframe["T"] - ln_new_T
        
        ax.semilogx(dataframe["R"], ln_new_T, label=f"ln fit pow={powers[i]}", color=colors[i])
        misfit_ax.semilogx(dataframe["R"], ln_misfit, label=f"ln misfit pow={powers[i]}", color=colors[i], ls="--")
        
        print(f"{powers[i]} :: {ln_fits}")
    
    # poly_fits, poly_errors = curve_fit(poly_fit_function, dataframe["R"], dataframe["T"])
    # poly_new_T = poly_fit_function(dataframe["R"], *poly_fits)
    # # ax.semilogx(dataframe["R"], poly_new_T, label="ln Fit", color="tab:red")
    # poly_misfit = dataframe["T"] - poly_new_T
    
    # misfit_ax.semilogx(dataframe["R"], ln_misfit, label="poly Misfit", color="tab:green")
    # # misfit_ax.semilogx(dataframe["R"], poly_misfit, label="ln Misfit", color="tab:purple")
    
    
    
    misfit_ax.set_ylabel(r"Misfit Temperature [$^\circ$C]")
    misfit_ax.legend(loc="lower left")
    ax.legend(loc="upper right")