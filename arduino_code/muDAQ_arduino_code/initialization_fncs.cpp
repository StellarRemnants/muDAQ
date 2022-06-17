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
#include "base_fncs.h"
#include "global_constants.h"
  
void begin_serial(unsigned long baudrate=DEFAULT_BAUDRATE) {
  Serial.begin(baudrate);
}

void wait_for_serial(int delay_duration) {
  while (Serial.available() == 0) {
    delay(delay_duration);
  }
}

bool check_for_restart_signal(byte restart_byte = DEFAULT_RESTART_BYTE) {
  if (Serial.available() == 0) {
    return false;
  }
  else {
    while (Serial.available() > 0) {
      byte read_byte = Serial.read();
      if (read_byte == restart_byte) {
        Serial.write(restart_byte);
        return true;
      }
    }
  }
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
      break;
    }
    else {
      Serial.write(reject_byte);
    }
  }
  
}


byte wait_for_byte_in_range(
  byte low_byte, 
  byte high_byte, 
  bool end_inclusive=true,
  byte confirm_byte = DEFAULT_CONFIRM_BYTE, 
  byte reject_byte = DEFAULT_REJECT_BYTE,
  unsigned long serial_delay = DEFAULT_SERIAL_DELAY
  ) {

  byte read_byte = 0;
  bool byte_valid = false;
  while (true) {
    wait_for_serial(serial_delay);
    read_byte = Serial.read();
    
    if (end_inclusive) {
      byte_valid = byte_in_range_incl(read_byte, low_byte, high_byte);
    }
    else {
      byte_valid = byte_in_range_excl(read_byte, low_byte, high_byte);
    }
    
    if (byte_valid) {
      Serial.write(confirm_byte);
      return read_byte;
    }
    else {
      Serial.write(reject_byte);
    }
  }
  
}

int get_single_pin_val(
  int num_valid_pins = NUM_VALID_PINS,
  int* valid_pin_array = VALID_PINS,
  unsigned long serial_delay = DEFAULT_SERIAL_DELAY,
  byte confirm_byte = DEFAULT_CONFIRM_BYTE, 
  byte reject_byte = DEFAULT_REJECT_BYTE
  ) {
  
  int read_int = 0;
  byte read_byte = 0x00;
  while (true) {
    wait_for_serial(serial_delay);
    read_byte = Serial.read();
    read_int = (int)(read_byte);
    if (int_in_array(
          read_int,
          num_valid_pins,
          valid_pin_array
          )
       ) {
        Serial.write(confirm_byte);
        return read_int;
    }
    else {
      Serial.write(reject_byte);
    }
  }
}
