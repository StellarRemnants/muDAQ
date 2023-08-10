#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 12:03:32 2022

@author: stellarremnants
"""

import threading
import os
import numpy as np
import time


test_file = "./test_file.csv"

start_called = False
start_time = None
def start_fnc(file_path, overwrite=True):
    if not start_called:
        global start_time
        start_time = time.time()
        if os.path.exists(file_path) and not overwrite:
            raise Exception("Test file already exists and overwrite is disabled!")
        else:
            with open(file_path, "w") as fdout:
                fdout.write(f"Initial_Time,{start_time:.7f}\n")
                fdout.write("TIMENOW,TIME_MUS,DATA,\n")
    else:
        pass
    
Total_Samples = 0
SAMPLE_CAP = int(1e5)
wait_time = 1e-3
write_lock = threading.Lock()
print_lock = threading.Lock()
def locked_printing(*args, **kwargs):
    print_lock.acquire()
    print(*args, **kwargs)
    print_lock.release()
    
print_file = "TEST_LOG.log"
with open(print_file, "w") as fdout:
    pass
def write_to_print_file_locked(phrase, end="\n"):
    print_lock.acquire()
    with open(print_file, "a") as fdout:
        fdout.write(f"{phrase}{end}")
    print_lock.release()
    
print_fnc = locked_printing


    
def run_fnc(file_path, thread_id, start_array, end_array):
    print_fnc(f"Starting thread#: {thread_id}")
    collect_continue = True
    start_array[thread_id] = 0
    global Total_Samples
    while np.sum(start_array) > 0:
        time.sleep(0.1)
    while collect_continue and end_array[thread_id]:
        data = np.random.rand()
        timenow = time.time() - start_time
        timenow_mus = int(timenow*1e6)
        
        write_lock.acquire(
            blocking=True,
            timeout=-1,
            )
            
        with open(test_file, "a") as fdout:
            fdout.write(
                f"{timenow:.7f},{timenow_mus},{data}\n"
                )
            write_lock.release()
            
        Total_Samples += 1    
        time.sleep(wait_time)
        if Total_Samples >= SAMPLE_CAP:
            collect_continue = False
            
        print_fnc(f"\rSamples: {Total_Samples}/{SAMPLE_CAP}", end="")
            
            
if __name__ == "__main__":
    start_fnc(test_file)
    NUM_THREADS = 10
    threads = []
    start_array = np.ones(NUM_THREADS)
    end_array = np.ones(NUM_THREADS)
    
    for i in range(NUM_THREADS):
        thread = threading.Thread(target=run_fnc, args=(test_file,i,start_array,end_array))
        threads.append(thread)
        
    for thread in threads:
        thread.start()
        
    # for thread in threads:
    #     thread.join()
    
    continue_collection = True
    
    
    status_lines = [
        "\rCollecting        ",
        "\rCollecting .      ",
        "\rCollecting . .    ",
        "\rCollecting . . .  ",
        "\rCollecting . . . .",
        ]
    status_count = len(status_lines)
    status_counter = 0
    try:
        while continue_collection:
            status_array = np.asarray([thread.is_alive() for thread in threads])
            if np.sum(status_array):
                print(status_lines[status_counter%status_count], end="")
                time.sleep(0.5)
                status_counter += 1
            else:
                continue_collection = False
                print("\rCompleted!          ")
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Closing Threads...")
        for i in range(NUM_THREADS):
            end_array[i] = 0
        time.sleep(0.5)
        status_array = [True]
        while np.sum(status_array):
            status_array = np.asarray([thread.is_alive() for thread in threads])
            open_threads = np.arange(NUM_THREADS)[status_array]
            print(f"\rOPEN THREADS: {', '.join(open_threads)}              ",end="")
            time.sleep(0.1)
        print("\rThreads closed.                                             ")
            
        
    # run_fnc(test_file)