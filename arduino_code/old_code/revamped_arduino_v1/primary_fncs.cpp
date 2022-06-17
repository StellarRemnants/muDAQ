/*
 * primary_fncs.cpp
 * Created:       2022-05-09
 * Last Modified: 2022-05-10
 * By: Joseph Lewis-Merrill
 * 
 * Description:
 *    Contains high level functions for the muDAQ program.
 */

#include <Arduino.h>
#include "initialization_fncs.h"

void setup_loop() {
  begin_serial();
  wait_for_specific_byte(0x31);
}

void main_loop() {
  
}
