/*
 * initialization_fncs.cpp
 * Created:       2022-05-09
 * Last Modified: 2022-05-10
 * By: Joseph Lewis-Merrill
 * 
 * Description:
 *    Contains declarations for functions in base_fncs.cpp
 */

#ifndef BASE_FNCS_H_INCLUDED
#define BASE_FNCS_H_INCLUDED

#include "global_constants.h"

struct daq_settings {
//  unsigned long baudrate = DEFAULT_BAUDRATE;
  int pin_count = 0;
  int* pin_array;
  unsigned long* times_array;
  int* adc_array; 
  unsigned long* pin_delays;
  unsigned long* pin_measurement_times;
  bool* pin_read_flag;
};

 void led_on();
 
 void led_off();
 
 bool byte_in_range_incl(
  byte test_byte, 
  byte low_byte, 
  byte high_byte
);

bool byte_in_range_excl(
  byte test_byte, 
  byte low_byte, 
  byte high_byte
);

bool int_in_array(
  int test_int,
  int array_length,
  int* array_pointer
);

bool* initialize_bool_array(int array_length);

int* initialize_int_array(int array_length);
unsigned long* initialize_ulong_array(int array_length);

int num_bytes_for_bytestring (unsigned long input_ulong);
byte* parse_ulong_into_bytes(
  unsigned long input_ulong, 
  int num_bytes
);
void serial_write_ulong(unsigned long input_ulong);

unsigned long get_val_from_serial(int byte_count);

unsigned long get_val_from_serial_by_count(
  int byte_count,
  int serial_delay = DEFAULT_SERIAL_DELAY,
  bool big_endian = true
  );
  
bool duration_elapsed(
  unsigned long last_micros, 
  unsigned long now_micros, 
  unsigned long duration
  );

#endif
