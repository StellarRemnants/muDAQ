/*
 * initialization_fncs.cpp
 * Created:       2022-05-09
 * Last Modified: 2022-05-10
 * By: Joseph Lewis-Merrill
 * 
 * Description:
 *    Contains low-level functions for initializing the muDAQ program.
 *    Called by higher-level functions in primary_fncs.cpp
 */



#include <Arduino.h>
#include "global_constants.h"
  
void begin_serial(unsigned long baudrate=DEFAULT_BAUDRATE) {
  Serial.begin(baudrate);
}

void wait_for_serial(int delay_duration) {
  while (Serial.available() == 0) {
    delay(delay_duration);
  }
}

bool check_for_restart_signal() {
  return false;
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

void wait_for_specific_byte(
  byte expected_byte, 
  byte confirm_byte = DEFAULT_CONFIRM_BYTE, 
  byte reject_byte = DEFAULT_REJECT_BYTE,
  unsigned long serial_delay = DEFAULT_SERIAL_DELAY
  ) {
  byte read_byte = 0;
  while (true) {
    wait_for_serial(serial_delay);
    read_byte = Serial.read();
    if (read_byte == expected_byte) {
      Serial.write(confirm_byte);
    }
    else {
      Serial.write(reject_byte);
    }
  }
}

void wait_for_byte_in_range(int lower_val, int upper_val, bool end_inclusive=false) {
  
}
