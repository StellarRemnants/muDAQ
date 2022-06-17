/*==================================================
 * TEMPLATE
 * Created:       2022-05-09
 * Last Modified: 2022-05-22
 * By: Joseph Lewis-Merrill
 * 
 * Description: 
 *    Contains declarations for functions in 
 *    runtime_fncs.cpp
 *==================================================
 */


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
 void read_and_write_adc(struct daq_settings* ds);


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
);
