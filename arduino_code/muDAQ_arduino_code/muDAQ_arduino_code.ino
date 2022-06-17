/*
 * Arduino program for muDAQ
 * Created:       2022-05-09
 * Last Modified: 2022-05-10
 * By: Joseph Lewis-Merrill
 * 
 * Description: 
 *    Manages Arduino board for reading selected ADC channels and
 *    transmits that information via serial. Accepts commands
 *    via serial from controller program.
 *    
 * Special thanks to Jewel Abbate
 */


#include "primary_fncs.h"
#include "base_fncs.h"

struct daq_settings global_daq_settings;

void setup() {
  global_daq_settings = setup_loop();
}

void loop() {
  main_loop(&global_daq_settings);
}
