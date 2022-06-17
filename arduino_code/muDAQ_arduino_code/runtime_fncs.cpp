/*
 * runtime_fncs.cpp
 * Created:       2022-05-09
 * Last Modified: 2022-05-10
 * By: Joseph Lewis-Merrill
 * 
 * Description: 
 *    Contains low-level functions for the muDAQ program post-initialization.
 *    Called by higher-level functions in primary_fncs.cpp
 */


/*
  struct daq_settings {
  unsigned long baudrate = DEFAULT_BAUDRATE;
  int pin_count = 0;
  int* pin_array;
  unsigned long* times_array;
  int* adc_array; 
};
 */
#include <Arduino.h>
#include "base_fncs.h"
#include "global_constants.h"

void read_adc(struct daq_settings* ds) {
  led_on();
  int num_pins = ds->pin_count;
  int* pin_array = ds->pin_array;
  bool read_this_pin = false;
  unsigned long start_micros = micros();
  unsigned long read_time = 0;
//  unsigned long time_delta = 0;
  unsigned long target_time = 0;
  for (int i = 0; i < num_pins; i++) {

    read_this_pin = duration_elapsed(
      ds->pin_measurement_times[i], 
      start_micros, 
      ds->pin_delays[i]
      );
    if (read_this_pin) {
      
      ds->adc_array[i] = analogRead(pin_array[i]);
      read_time = micros();
//      time_delta = read_time - ds->times_array[i];
      ds->times_array[i] = read_time;
      target_time = start_micros - ds->pin_delays[i];
      while (ds->pin_measurement_times[i] < target_time) {
        ds->pin_measurement_times[i] += ds->pin_delays[i];
      }
      ds->pin_read_flag[i] = true;
      
      
//      Serial.print(ds->pin_array[i]);
//      Serial.print("::");
//      Serial.print(ds->pin_delays[i]);
//      Serial.print("::");
//      Serial.print(read_time);
//      Serial.print("::");
//      Serial.print(time_delta);
//      Serial.print("::");
//      Serial.print(ds->pin_measurement_times[i]);
//      Serial.println("::");
    }
  }
  led_off();
}

/*
  struct daq_settings {
  unsigned long baudrate = DEFAULT_BAUDRATE;
  int pin_count = 0;
  int* pin_array;
  unsigned long* times_array;
  int* adc_array; 
  unsigned long* pin_delays;
  unsigned long* pin_measurement_times;
  bool* pin_read_flag;
};
 */

void print_daq_settings(struct daq_settings* ds) {
  for (int i = 0; i < ds->pin_count; i++) {
    Serial.print(ds->pin_array[i]);
    Serial.print(",");
    Serial.print(ds->times_array[i]);
    Serial.print(",");
    Serial.print(ds->adc_array[i]);
    Serial.print(",");
    Serial.print(ds->pin_delays[i]);
    Serial.print(",");
    Serial.print(ds->pin_measurement_times[i]);
    Serial.print(",");
    Serial.print(ds->pin_read_flag[i]);
    Serial.println(";");
  }
  led_off();
}

void read_and_write_adc(struct daq_settings* ds) {
  read_adc(ds);
  int num_pins = ds->pin_count;
  int* pin_array = ds->pin_array;
  unsigned long* times_array = ds->times_array;
  int* adc_array = ds->adc_array;

  while (!Serial.availableForWrite()){
    delay(DEFAULT_SERIAL_DELAY);
  }
  bool printed_a_pin = false;
  for (int i = 0; i < num_pins; i++) {
    if (ds->pin_read_flag[i]) {
      Serial.write(pin_array[i]);
      Serial.print(VAL_SEPARATOR);
      serial_write_ulong(times_array[i]);
      Serial.print(VAL_SEPARATOR);
      serial_write_ulong((unsigned long)(adc_array[i]));
      if (i < num_pins-1) {
        Serial.print(CH_SEPARATOR);
      }
//      print_daq_settings(ds);
      ds->pin_read_flag[i] = false;
      printed_a_pin = true;
    }
  }
  if (printed_a_pin) {
    Serial.print(MSG_TERMINATOR);
  }
}

int restart_counter = 0;
bool check_for_restart_signal(
  byte restart_byte = DEFAULT_RESTART_BYTE,
  int restart_count = DEFAULT_RESTART_COUNT,
  byte reject_byte = DEFAULT_REJECT_BYTE
  ){
    
  bool restart_indicated = false;
  byte read_byte = 0x00;
  while (Serial.available() > 0) {
    read_byte = Serial.read();
    if (read_byte == restart_byte) {
      restart_counter++;
      if (restart_counter >= restart_count) {
        restart_indicated = true;
        restart_counter = 0;
      }
    }
    else if (read_byte == reject_byte) {
      restart_counter = 0;
      restart_indicated = false;
    }
  }
  return restart_indicated;
  
}
