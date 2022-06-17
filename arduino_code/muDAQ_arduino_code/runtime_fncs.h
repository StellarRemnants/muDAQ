/*
 * TEMPLATE
 * Created:       2022-05-09
 * Last Modified: 2022-05-10
 * By: Joseph Lewis-Merrill
 * 
 * Description: 
 *    Contains declarations for functions in runtime_fncs.cpp
 */

 void read_and_write_adc(struct daq_settings* ds);
 
 bool check_for_restart_signal(
  byte restart_byte = DEFAULT_RESTART_BYTE,
  int restart_count = DEFAULT_RESTART_COUNT,
  byte reject_byte = DEFAULT_REJECT_BYTE
  );
