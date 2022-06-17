/*==================================================
 * primary_fncs.cpp
 * Created:       2022-05-09
 * Last Modified: 2022-05-22
 * By: Joseph Lewis-Merrill
 * 
 * Description:
 *    Contains high level functions for the muDAQ 
 *      program.
 *==================================================
 */


#include <Arduino.h>
#include "base_fncs.h"
#include "initialization_fncs.h"
#include "runtime_fncs.h"


/*--------------------------------------------------
 * Type: Function
 * struct daq_settings setup_loop()
 *  Initializes the muDAQ program based on input 
 *    from the serial controller program. Returns a
 *    struct which contains the program settings and
 *    data arrays. See struct daq_settings under
 *    base_fncs.h for morer information on the 
 *    struct. 
 *  
 *  Arguments:
 *    None
 *    
 *  Returns
 *    struct daq_settings ret_settings
 *      -> Struct containing program settings and 
 *          data arrays for program.
 *--------------------------------------------------
 */
struct daq_settings setup_loop() {

  // Allocate struct to be returned
  struct daq_settings ret_settings;

  // Get pin count
  begin_serial();
  wait_for_specific_byte(DEFAULT_CONNECT_BYTE);
  byte pin_count_byte = wait_for_byte_in_range(MIN_VALID_PIN_COUNT, MAX_VALID_PIN_COUNT);
  int pin_count = (int)(pin_count_byte);

  // Allocate and initialize values in struct
  ret_settings.pin_count = pin_count;
  ret_settings.times_array = initialize_ulong_array(pin_count);
  ret_settings.adc_array = initialize_ulong_array(pin_count);
  ret_settings.pin_delays = initialize_ulong_array(pin_count);
  ret_settings.pin_measurement_times = initialize_ulong_array(pin_count);
  ret_settings.pin_read_flag = initialize_bool_array(pin_count);
  ret_settings.pin_array = initialize_int_array(pin_count);

  // Get each pin id   
  for (int i = 0; i < pin_count; i++) {
    ret_settings.pin_array[i] = get_single_pin_val();
  }

  // Get the sample delay for each pin
  for (int i = 0; i < pin_count; i++ ) {
    ret_settings.pin_delays[i] = get_val_from_serial_by_count(4);
  }

  // ONLY FOR ATP: Set the read resolution to 14. Comment out for UNO, RedBoard, and similar
  //analogReadResolution(14);

  // Return struct for use throughout program
  return ret_settings;
  
}


/*--------------------------------------------------
 * Type: Function
 * bool main_loop(struct daq_settings*)
 *  Data collection loop run after initialization
 *    is completed. First checks whether a restart
 *    has been requested. If not, runs 
 *    read_and_write_adc(), which reads each pin 
 *    that has not been read for at least its 
 *    corresponding pin delay and then reports the
 *    read values via serial.
 *  
 *  Arguments:
 *    struct daq_settings* global_daq_settings 
 *      -> Pointer to the global daq_settings struct
 *          which allows modification of its values
 *          by subfunctions.
 *    
 *  Returns
 *    bool
 *      -> true:  Restart requested
 *      -> false: No restart requested
 *--------------------------------------------------
 */
bool main_loop(struct daq_settings* global_daq_settings) {

  // Check for restart signal
  bool restart_indicated = false;
  restart_indicated = check_for_restart_signal();

  // If restart, report back immediately
  if (restart_indicated) {
    return true;
  }

  // If no restart, read pins and report via serial
  else {
    read_and_write_adc(global_daq_settings);
    return false;
  }
  
}
