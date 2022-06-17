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
#include "base_fncs.h"
#include "initialization_fncs.h"
#include "runtime_fncs.h"



struct daq_settings setup_loop() {
  struct daq_settings ret_settings;
  begin_serial();
  wait_for_specific_byte(DEFAULT_CONNECT_BYTE);
  byte pin_count_byte = wait_for_byte_in_range(MIN_VALID_PIN_COUNT, MAX_VALID_PIN_COUNT);
  int pin_count = (int)(pin_count_byte);
  
  ret_settings.pin_count = pin_count;
  ret_settings.times_array = initialize_ulong_array(pin_count);
  ret_settings.adc_array = initialize_int_array(pin_count);
  ret_settings.pin_delays = initialize_ulong_array(pin_count);
  ret_settings.pin_measurement_times = initialize_ulong_array(pin_count);
  ret_settings.pin_read_flag = initialize_bool_array(pin_count);

  int* pin_array = initialize_int_array(pin_count);
  
  for (int i = 0; i < pin_count; i++) {
    pin_array[i] = get_single_pin_val();
  }
  ret_settings.pin_array = pin_array;

  for (int i = 0; i < pin_count; i++ ) {
    ret_settings.pin_delays[i] = get_val_from_serial_by_count(4);
  }
  
  return ret_settings;
}

bool restart_indicated = false;
void main_loop(struct daq_settings* global_daq_settings) {
  restart_indicated = check_for_restart_signal();
  if (restart_indicated) {
    *global_daq_settings = *&setup_loop();
    restart_indicated = false;
  }
  read_and_write_adc(global_daq_settings);
}
