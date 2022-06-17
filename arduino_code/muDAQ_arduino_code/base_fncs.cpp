/*
 * base_fncs.cpp
 * Created:       2022-05-09
 * Last Modified: 2022-05-10
 * By: Joseph Lewis-Merrill
 * 
 * Description:
 *    Contains base-level functions use throughout the muDAQ program.
 */

#include <Arduino.h>
#include "global_constants.h"

//struct daq_settings {
//  unsigned long baudrate = DEFAULT_BAUDRATE;
//  int pin_count = 0;
//  int* pin_array;
//  unsigned long* times_array;
//  int* adc_array; 
//};

bool led_initialized = false;

void initialize_led() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
}

void led_on() {
  if (!led_initialized) {
    initialize_led();
  }
  digitalWrite(LED_BUILTIN, HIGH);
}

void led_off() {
  if (!led_initialized) {
    initialize_led();
  }
  digitalWrite(LED_BUILTIN, LOW);
  
}


bool byte_in_range_incl(
  byte test_byte, 
  byte low_byte, 
  byte high_byte
  ) {
    
  if ((test_byte <= high_byte) && (test_byte >= low_byte)) {
    return true;
  }
  else {
    return false;
  }
  
}

bool byte_in_range_excl(
  byte test_byte, 
  byte low_byte, 
  byte high_byte
  ) {
    
  if ((test_byte < high_byte) && (test_byte > low_byte)) {
    return true;
  }
  else {
    return false;
  }
  
}

bool int_in_array(
  int test_int,
  int array_length,
  int* array_pointer
  ) {
    
  for (int i = 0; i < array_length; i++) {
    if (test_int == array_pointer[i]) {
      return true; 
    }
  }
  return false;
    
}

bool* initialize_bool_array(int array_length) {
  bool* bool_array = new bool[array_length];
  for (int i = 0; i < array_length; i++) {
    bool_array[i] = false;
  }
  return bool_array;
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

float LOG_BASE_CONSTANT = 1/log(float(256));
int num_bytes_for_bytestring (unsigned long input_ulong) {
  return ceil(log(input_ulong)*LOG_BASE_CONSTANT);
}

byte* parse_ulong_into_bytes(
  unsigned long input_ulong, 
  int num_bytes
  ){

  unsigned long rem = 0;
  unsigned long num = input_ulong;

  

  static byte* byte_array = new byte[num_bytes];
  for (int i = 0; i < num_bytes; i++) {
    byte_array[i] = 0x00;
  }

  for (int byte_index = num_bytes - 1; byte_index >= 0; byte_index--) {
    rem = num % 256;
    byte_array[byte_index] = byte(rem);
    num = (num-rem) / 256;
  }
  
  return byte_array;
}

void serial_write_ulong(unsigned long input_ulong) {
  int num_bytes = num_bytes_for_bytestring(input_ulong);
  byte* byte_array = parse_ulong_into_bytes(input_ulong, num_bytes);
  for (int i = 0; i < num_bytes; i++) {
    Serial.write(byte_array[i]);
  }
}

const unsigned long ULONG_BASE_CONSTANTS[] = {
  1,
  256,
  65536,
  16777216,
//  4294967296,
//  1099511627776,
//  281474976710656,
//  72057594037927936,
};




unsigned long get_val_from_serial_by_count(
  int byte_count,
  int serial_delay = DEFAULT_SERIAL_DELAY,
  bool big_endian = true
  ) {

  byte byte_array[byte_count];
  for (int i = 0; i < byte_count; i++) {
    byte_array[i] = 0;
  }
  
  while (!(Serial.available() >= byte_count)) {
    delay(serial_delay);
  }

  for (int i = 0; i < byte_count; i++) {
    byte_array[i] = Serial.read();
  }

  unsigned long ret_val = 0;
  int index = 0;
  unsigned long multiplier_val = 0;
  unsigned long addendum = 0;
  for (int i = 0; i < byte_count; i++) {
    if (big_endian) {
      index = byte_count - i - 1;
    }
    else {
      index = i;
    }
    multiplier_val = (unsigned long)(byte_array[i]);
    addendum = (ULONG_BASE_CONSTANTS[index] * multiplier_val);
    ret_val += addendum;
  
  }
  for (int i = 0; i < byte_count; i++) {
    Serial.print(byte_array[i], HEX);
    Serial.print(".");
  }
  Serial.print(",");
  Serial.println(ret_val);
  return ret_val;
}

bool duration_elapsed(
  unsigned long last_micros, 
  unsigned long now_micros, 
  unsigned long duration
  ) {

    unsigned long elapsed = 0;
    if (now_micros < last_micros) {
      // Rollover has occurred!
      elapsed = (4294967295 - last_micros) + now_micros;
    }
    else {
      elapsed = now_micros - last_micros;
    }

    if (elapsed >= duration) {
      return true;
    }
    else {
      return false;
    }
}
  
