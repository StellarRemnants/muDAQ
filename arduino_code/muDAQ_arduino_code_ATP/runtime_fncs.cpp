/*==================================================
 * runtime_fncs.cpp
 * Created:       2022-05-09
 * Last Modified: 2022-08-17
 * By: Joseph Lewis-Merrill
 * 
 * Description: 
 *    Contains low-level functions for the muDAQ 
 *      program post-initialization. Called by 
 *      higher-level functions in primary_fncs.cpp
 *==================================================
 */


#include <Arduino.h>
#include "base_fncs.h"
#include "global_constants.h"


/*--------------------------------------------------
 * Type: Function
 * void read_adc(struct daq_settings*)
 *  For each pin, checks if the appropriate duration
 *    has elapsed and, if so, read the ADC value for
 *    that pin. If a value is read, the flag for 
 *    that pin is set to true.
 *  
 *  Arguments:
 *    struct daq_settings* ds
 *      -> Pointer to the global daq_settings struct
 *          used to pass adc information on.
 *    
 *  Returns
 *    None
 *--------------------------------------------------
 */
void read_adc(struct daq_settings* ds) {

  // Turn LED on to indicate a read is occuring
  led_on();

  // Allocate and (where needed) initialize variables
  int num_pins = ds->pin_count;
  int* pin_array = ds->pin_array;
  bool read_this_pin = false;
  unsigned long start_micros = micros();
  unsigned long read_time = 0;
  unsigned long target_time = 0;

  // For each pin in pin_array
  for (int i = 0; i < num_pins; i++) {

    // Check whether the pin needs to be read based on time elapsed
    read_this_pin = duration_elapsed(
      ds->pin_measurement_times[i], 
      start_micros, 
      ds->pin_delays[i]
      );
      
    if (read_this_pin) {
      // If the pin needs to be read, read the pin and record the time
      ds->adc_array[i] = analogRead(pin_array[i]);
      read_time = micros();
      ds->times_array[i] = read_time;

      // Increment the last measurement time by the pin's delay
      //   until it is the largest multiple of the pin delay
      //   less than the time this data collection cycle began.
      //   Keeps sample spacing as close to pin delay as possible
      //   with minimal overhead.
      target_time = start_micros - ds->pin_delays[i];
      if (ds->pin_measurement_times[i] > target_time) { //Added to fix rollover sample spacing issue (2022-08-17, Lewis-Merrill)
        ds->pin_measurement_times[i] = 0;
      }
      while (ds->pin_measurement_times[i] < target_time) {
        ds->pin_measurement_times[i] += ds->pin_delays[i];
      }
      ds->pin_read_flag[i] = true;
    }
  }
  led_off();
  
}

/*--------------------------------------------------
 * Type: Function
 * void print_daq_settings(struct daq_settings*)
 *  Prints the contents of the daq_settings struct 
 *    to serial in a human-readable format. Not used
 *    under normal operation, but useful for 
 *    debugging when something inevitably goes 
 *    wrong. Will interfere with the controller code
 *    read if left on.
 *  
 *  Arguments:
 *    struct daq_settings* ds
 *      -> Pointer to the global daq_settings struct
 *          used to print the information therein.
 *    
 *  Returns
 *    None
 *--------------------------------------------------
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
  
}

/*--------------------------------------------------
 * Type: Function
 * void read_and_write_adc(struct daq_settings*)
 *  TEMPLATE
 *  
 *  Arguments:
 *    struct daq_settings* ds
 *      -> Pointer to the global daq_settings struct
 *          as needed to both write data that is 
 *          read from analog and forward said data 
 *          to serial.
 *          
 *          
 *  Message format:
 *  
 *    With
 *      CH_SEPARATOR    = ";"
 *      VAL_SEPARATOR   = ","
 *      MSG_TERMINATOR  = "\r\n"
 *  
 *    "<CH1>,<Time1>,<ADC1>;<CH2>,<Time2>,<ADC2>;
 *    [...];<CHn>,<Timen>,<ADCn>;\r\n"
 *    
 *    Where:
 *      <CH#> 
 *        -> Pin id for the (#)th channel printed,
 *            converted to a single byte.
 *    
 *      <Time#>
 *        -> Time in microseconds for the (#)th
 *            channel printed, converted to a string
 *            of 1 to 4 bytes (big-endian).
 *            
 *      <ADC#>
 *        -> The value read from the ADC for the 
 *            (#)th pin, converted to a string of
 *            1 to 4 bytes (big-endian).
 *    
 *  Returns
 *    None
 *--------------------------------------------------
 */
void read_and_write_adc(struct daq_settings* ds) {

  // Get ADC values
  read_adc(ds);

  // Initialize values
  int num_pins = ds->pin_count;
  bool printed_a_pin = false;

  // For each pin
  for (int i = 0; i < num_pins; i++) {

    // Check if the pin has been read
    if (ds->pin_read_flag[i]) {

      // If so, write the values out via serial
      Serial.write(ds->pin_array[i]);
      Serial.print(VAL_SEPARATOR);
      serial_write_ulong(ds->times_array[i]);
      Serial.print(VAL_SEPARATOR);
      serial_write_ulong((ds->adc_array[i]));
      Serial.print(CH_SEPARATOR);

      // Flag that a pin has been printed
      printed_a_pin = true;

      // Set the pin's read flag to false now that it has been printed
      ds->pin_read_flag[i] = false;
    }
  }
  // If at least one pin has been printed, print a message terminator
  if (printed_a_pin) {
    Serial.print(MSG_TERMINATOR);
  }
  
}

/*--------------------------------------------------
 * Type: Variable
 * int restart_counter
 *  Keeps track of the number of times a restart
 *    byte has been received since the last restart
 *    or the last cancellation of restart.
 *--------------------------------------------------
 */
int restart_counter = 0;

/*--------------------------------------------------
 * Type: Function
 * bool check_for_restart_signal([byte, int, byte])
 *  Checks for bytes in the serial input buffer. For
 *    each restart_byte found, increment 
 *    restart_counter. For each reject_byte, reset 
 *    restart_counter to 0. For any other byte, send
 *    reject_byte. If restart_counter reaches 
 *    restart_count, return true. Otherwise, returns
 *    false.
 *  
 *  Arguments:
 *    byte restart_byte 
 *      -> Increments the restart counter by 1 when 
 *          received. Should be unique to avoid any
 *          potential mixups.
 *    
 *    int restart_count
 *      -> The number of times restart_byte needs to
 *          be received to trigger a restart. This
 *          is cumulative unless reset by receiving
 *          a reject_byte.
 *    
 *    byte reject_byte
 *      -> Byte sent when any byte other than 
 *          restart_byte or itself (reject_byte) are
 *          received. When received, resets the
 *          counter restart_counter to 0.
 *    
 *  Returns
 *    bool
 *      -> true:  Restart indicated
 *      -> false: No restart indicated
 *--------------------------------------------------
 */
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
