/*
 * initialization_fncs.h
 * Created:       2022-05-09
 * Last Modified: 2022-05-10
 * By: Joseph Lewis-Merrill
 * 
 * Description: 
 *    Contains declarations for functions in initialization_fncs.cpp
 */

 #include <Arduino.h>
 #include "global_constants.h"

void begin_serial(unsigned long baudrate=DEFAULT_BAUDRATE);

void wait_for_specific_byte(
  byte expected_byte, 
  byte confirm_byte = DEFAULT_CONFIRM_BYTE, 
  byte reject_byte = DEFAULT_REJECT_BYTE,
  unsigned long serial_delay = DEFAULT_SERIAL_DELAY
);
