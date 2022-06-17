/*==================================================
 * initialization_fncs.cpp
 * Created:       2022-05-09
 * Last Modified: 2022-05-22
 * By: Joseph Lewis-Merrill
 * 
 * Description:
 *    Contains declarations for functions in 
 *      base_fncs.cpp
 *==================================================
 */


#ifndef BASE_FNCS_H_INCLUDED //Prevents redefining values
#define BASE_FNCS_H_INCLUDED


#include "global_constants.h"


/*--------------------------------------------------
 * Type: Struct
 * struct daq_settings
 *  Used to contains daq settings and data in a
 *    compact, easily transferred form. Created by 
 *    setup_loop() in primary_fncs.cpp and 
 *  
 *  Contains:
 *    int pin_count
 *      -> Number of analog pins to be read. Used
 *          to allocate, read from, and write to
 *          the other arrays in the struct.
 *    
 *    int* pin_array
 *      -> Array containing the pin id integers
 *          corresponding to the analog pins to
 *          be sampled.
 *    
 *    unsigned long* times_array
 *      -> Array containing the time in microseconds 
 *          that the pins were last sampled.
 *    
 *    unsigned long* adc_array
 *      -> Array containing the values, as reported
 *          by the ADC, the pins had when last
 *          sampled.
 *    
 *    unsigned long* pin_delays
 *      -> Array containing the time in microseconds
 *          the should be waited between samples for
 *          each channel. Effectively sets the 
 *          samplerate per channel. Delays lower 
 *          than the value corresponding to the 
 *          maximum sample frequency will result in
 *          sampling at the maximum frequency.
 *    
 *    unsigned long* pin_measurement_times
 *      -> Array containing the time in microseconds
 *          marking the beginning of the read cycle
 *          in which the pin was last read. This is 
 *          distinct from the values in times_array
 *          as those values are when the pin was 
 *          actually read, not the beginning of the
 *          read cycle in which they were read.
 *    
 *    bool* pin_read_flag
 *      -> Array containing flags indicating for
 *          each pin whether it has been sampled
 *          since the last time values were reported 
 *          via serial. Set true when sampled, set
 *          false when values printed via serial.
 *  
 *--------------------------------------------------
 */
struct daq_settings {
  int pin_count = 0;
  int* pin_array;
  unsigned long* times_array;
  unsigned long* adc_array; 
  unsigned long* pin_delays;
  unsigned long* pin_measurement_times;
  bool* pin_read_flag;
};


/*--------------------------------------------------
 * Type: Function
 * void led_on()
 *  Sets the builtin LED to HIGH (on)
 *  
 *  Arguments:
 *    None
 *    
 *  Returns
 *    None
 *--------------------------------------------------
 */
void led_on();


/*--------------------------------------------------
 * Type: Function
 * void led_off()
 *  Sets the builtin LED to LOW (off)
 *  
 *  Arguments:
 *    None
 *    
 *  Returns
 *    None
 *--------------------------------------------------
 */
void led_off();


/*--------------------------------------------------
 * Type: Function
 * bool byte_in_range_incl(byte, byte, byte)
 *  Check if test_byte is in between low_byte and 
 *    high_byte inclusively.
 *  
 *  Arguments:
 *    byte test_byte 
 *      -> byte to check
 *      
 *    byte low_byte  
 *      -> lower bound [incl.]
 *      
 *    byte high_byte 
 *      -> upper bound [incl.]
 *  
 *  Returns 
 *    bool
 *    -> true:  if in range
 *       false: if not in range
 *--------------------------------------------------
 */
bool byte_in_range_incl(
  byte test_byte, 
  byte low_byte, 
  byte high_byte
);


/*--------------------------------------------------
 * Type: Function
 * bool byte_in_range_excl(byte, byte, byte)
 *  Check if test_byte is in between low_byte and 
 *    high_byte exclusively
 *  
 *  Arguments:
 *    byte test_byte 
 *      -> byte to check
 *      
 *    byte low_byte  
 *      -> lower bound [excl.]
 *      
 *    byte high_byte 
 *      -> upper bound [excl.]
 *  
 *  Returns 
 *    bool
 *    -> true:  if in range
 *       false: if not in range
 *--------------------------------------------------
 */
bool byte_in_range_excl(
  byte test_byte, 
  byte low_byte, 
  byte high_byte
);


/*--------------------------------------------------
 * Type: Function
 * bool int_in_array(int, int, const int*)
 *  Checks if test_int is the same as any values in
 *    the const int array given by array_pointer
 *  Used by get_single_pin_val() in 
 *    initialization_fncs.cpp to validate pins
 *  
 *  Arguments:
 *    int test_int             
 *      -> value to check
 *      
 *    int array_length         
 *      -> length of array
 *      
 *    const int* array_pointer 
 *      -> pointer to array
 *    
 *  Returns 
 *    bool
 *    -> true:  test_int found
 *       false: test_int not found
 *--------------------------------------------------
 */
bool int_in_array(
  int test_int,
  int array_length,
  const int* array_pointer
);


/*--------------------------------------------------
 * Type: Function
 * bool* initialize_bool_array(int[, bool])
 *  Create a new bool array of length array_length 
 *    and initialize all values within to the value 
 *    given by init_val.
 *  
 *  Arguments:
 *    int array_length 
 *      -> length of the array to be created
 *      
 *    bool init_val
 *      -> value to initialize all entries in array
 *    
 *  Returns
 *    unsigned long*
 *      -> pointer to the initialized array
 *--------------------------------------------------
*/
bool* initialize_bool_array(
  int array_length,
  bool init_val = false
  );


/*--------------------------------------------------
 * Type: Function
 * int* initialize_int_array(int[, int])
 *  Create a new int array of length array_length 
 *    and initialize all values within to the value 
 *    given by init_val.
 *  
 *  Arguments:
 *    int array_length 
 *      -> length of the array to be created
 *      
 *    int init_val
 *      -> value to initialize all entries in array
 *    
 *  Returns
 *    unsigned long*
 *      -> pointer to the initialized array
 *--------------------------------------------------
*/
int* initialize_int_array(
  int array_length,
  int init_val = 0
  );


/*--------------------------------------------------
 * Type: Function
 * unsigned long* initialize_ulong_array(int[, unsigned long])
 *  Create a new unsigned long array of length
 *    array_length and initialize all values within 
 *    to the value given by init_val.
 *  
 *  Arguments:
 *    int array_length 
 *      -> length of the array to be created
 *      
 *    unsigned long init_val
 *      -> value to initialize all entries in array
 *    
 *  Returns
 *    unsigned long*
 *      -> pointer to the initialized array
 *--------------------------------------------------
 */
unsigned long* initialize_ulong_array(
  int array_length,
  unsigned long init_val = 0
  );


/*--------------------------------------------------
 * Type: Function
 * int num_bytes_for_bytestring()
 *  Calculate the minimum number of bytes needed to
 *    represent input_ulong as a bytestring.
 *  
 *  Arguments:
 *    unsigned long input_ulong 
 *      -> value to be represented as bytes
 *    
 *  Returns
 *    int
 *      -> number of bytes needed. Will always be
 *          between 1 and 4 (incl.)
 *--------------------------------------------------
 */
int num_bytes_for_bytestring (unsigned long input_ulong);


/*--------------------------------------------------
 * Type: Function
 * void parse_ulong_into_bytes(unsigned long, int, byte*)
 *  Break input_ulong into bytes and place the 
 *    values into the preallocated array byte_array
 *  
 *  Arguments:
 *    unsigned long input_ulong 
 *      -> value to break into bytes 
 *      
 *    int num_bytes
 *      -> number of bytes to break the value into.
 *          Can be calculated with 
 *          num_bytes_for_bytestring()
 *          
 *    byte* byte_array
 *      -> byte array in which to place the values.
 *          Should be allocated beforehand.
 *    
 *  Returns
 *    None
 *--------------------------------------------------
 */
byte* parse_ulong_into_bytes(
  unsigned long input_ulong, 
  int num_bytes
);


/*--------------------------------------------------
 * Type: Function
 * void serial_write_ulong(unsigned long[, bool])
 *  Break an unsigned long into bytes using 
 *    parse_ulong_into_bytes() and transmit it over
 *    serial.
 *  
 *  Arguments:
 *    unsigned long input_ulong 
 *      -> Value to be parsed and transmitted
 *     
 *    bool big_endian
 *      -> Order to transmit bytes:
 *          true : most significant first
 *          false: least significant first
 *    
 *  Returns
 *    None
 *--------------------------------------------------
 */
void serial_write_ulong(
  unsigned long input_ulong,
  bool big_endian = true
);

/*--------------------------------------------------
 * Type: Function
 * unsigned long get_val_from_serial_by_count(int[, int, bool])
 *  Reads a value from serial with a predetermined
 *    number of bytes and places the value into an
 *    unsigned long. Used to get the sample delays
 *    for each pin in the initialization process.
 *  
 *  Arguments:
 *    int byte_count    
 *      -> number of bytes to read
 *      
 *    int serial_delay  
 *      -> period in milliseconds to delay while
 *          waiting for bytes to read. Higher values
 *          have lower CPU cost but higher latency.
 *          
 *    bool big_endian   
 *      -> order of bytes. If true, interpret as 
 *          most significant first (default). 
 *          Otherwise, least significant first.
 *    
 *  Returns
 *    unsigned long 
 *      -> The value read from serial
 *--------------------------------------------------
 */
unsigned long get_val_from_serial_by_count(
  int byte_count,
  int serial_delay = DEFAULT_SERIAL_DELAY,
  bool big_endian = true
);


/*--------------------------------------------------
 * Type: Function
 * bool duration_elapsed(unsigned long, unsigned long, unsigned long)
 *  Checks if now_micros is at least duration
 *    greater than last_micros. Includes protections
 *    against the max unsigned long rollover that
 *    occurs about every 70 minutes when 
 *    representing time as microseconds.
 *  
 *  Arguments:
 *    unsigned long last_micros 
 *      -> previous time in microseconds
 *      
 *    unsigned long now_micros  
 *      -> current time in microseconds
 *      
 *    unsigned long duration    
 *      -> duration to check for in microseconds
 *    
 *  Returns
 *    bool -> true if duration has elapsed
 *            false otherwise
 *--------------------------------------------------
 */
bool duration_elapsed(
  unsigned long last_micros, 
  unsigned long now_micros, 
  unsigned long duration
);


#endif
