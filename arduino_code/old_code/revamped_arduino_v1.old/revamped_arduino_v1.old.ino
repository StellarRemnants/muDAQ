/*
 * Arduino program for muDAQ
 * Created:       2022-05-09
 * Last Modified: 2022-05-09
 * By: Joseph Lewis-Merrill
 * 
 * Description: 
 *    Manages Arduino board for reading selected ADC channels and
 *    transmitting that information via serial. Accepts commands
 *    via serial from controller program.
 *    
 * Special thanks to Jewel Abbate
 */


#include "primary_fncs.h"


void setup() {
  setup_loop();
}

void loop() {
  main_loop();
}
