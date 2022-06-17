/*
 * initialization_fncs.cpp
 * Created:       2022-05-09
 * Last Modified: 2022-05-09
 * By: Joseph Lewis-Merrill
 * 
 * Description:
 *    Contains low-level functions for initializing the muDAQ program.
 *    Called by higher-level functions in primary_fncs.cpp
 */


#include <Arduino.h>
#include "global_constants.h"


void begin_serial(unsigned long baudrate) {
  
}

void led_on() {
  
}

void led_off() {
  
}

void wait_for_serial(int delay_duration) {
  
}

bool check_for_restart_signal() {
  
}

int* initialize_int_array(int array_length) {
  int* int_array = new int[array_length];
  for (int i = 0; i<array_length; i++) {
    int_array[i] = 0;
  }
  return int_array;
}

unsigned long* initialize_ulong_array(int array_length) {
  unsigned long* ulong_array = new unsigned long[array_length];
  for (int i = 0; i<array_length; i++) {
    ulong_array[i] = 0;
  }
  return ulong_array;
  
}
