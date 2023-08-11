#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 15:03:29 2023

@author: stellarremnants
"""

import time

def write_file(file_path, write_string):
    with open(file_path, "a") as fdout:
        fdout.write(write_string)
        
if __name__ == "__main__":
    start_time = time.time()
    target_time_delta = 1
    target_time = start_time
    try:
        while True:
            
            current_time = time.time()
            write_string = f"{current_time}\n"
            write_file("test.log", write_string)
            
            while target_time < current_time:
                target_time += target_time_delta
            
            time.sleep(target_time - time.time())
    except KeyboardInterrupt:
        pass
    