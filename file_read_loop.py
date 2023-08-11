#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 15:12:53 2023

@author: stellarremnants
"""

import time

def open_read_file(file_path):
    fdin = open(file_path, "r")
    return fdin

def close_read_file(fdin):
    if not fdin.closed:
        fdin.close()
        
def readline_pause(fdin, max_wait_time=5, sleep_pause = 0.01):
    start_time = time.time()
    readline = ""
    while True:
        readline = fdin.readline()
        if not(len(readline)):
            if time.time() - start_time > max_wait_time:
                return False
            else:
                time.sleep(sleep_pause)
        else:
            return readline
        
if __name__ == "__main__":
    fdin = open_read_file("test.log")
    try:
        while True:
            readline = readline_pause(fdin, max_wait_time=5, sleep_pause=0.01)
            if readline == False:
                print("READLINE TIMED OUT")
            else:
                print(readline, end="")
    except KeyboardInterrupt:
        pass
    
    close_read_file(fdin)