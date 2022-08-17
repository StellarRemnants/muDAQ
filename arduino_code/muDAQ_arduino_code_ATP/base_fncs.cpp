/*==================================================
 * base_fncs.cpp
 * Created:       2022-05-09
 * Last Modified: 2022-08-17
 * By: Joseph Lewis-Merrill
 * 
 * Description:
 *    Contains base-level functions use throughout 
 *      the muDAQ program.
 *==================================================
 */


#include <Arduino.h>
#include "global_constants.h"


/*--------------------------------------------------
 * Type: Variable
 * bool led_initialized
 *  Used by led_on() and led_off() to check if
 *    LED has been initialized yet. If not, calls
 *    initialize_led(), which sets it to true.
 *--------------------------------------------------
 */
bool led_initialized = false;


/*--------------------------------------------------
 * Type: Function
 * void initialize_led()
 *  Prepares the builtin LED for use.
 *  
 *  Arguments:
 *    None
 *    
 *  Returns
 *    None
 *--------------------------------------------------
 */
void initialize_led() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
}


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
void led_on() {
  if (!led_initialized) {
    initialize_led();
  }
  digitalWrite(LED_BUILTIN, HIGH);
}


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
void led_off() {
  if (!led_initialized) {
    initialize_led();
  }
  digitalWrite(LED_BUILTIN, LOW);
  
}


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
  ) {
    
  if ((test_byte <= high_byte) && (test_byte >= low_byte)) {
    return true;
  }
  else {
    return false;
  }
  
}


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
  ) {
    
  if ((test_byte < high_byte) && (test_byte > low_byte)) {
    return true;
  }
  else {
    return false;
  }
  
}


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
  ) {
    
  for (int i = 0; i < array_length; i++) {
    if (test_int == array_pointer[i]) {
      return true; 
    }
  }
  return false;
    
}


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
  ) {
  bool* bool_array = new bool[array_length];
  for (int i = 0; i < array_length; i++) {
    bool_array[i] = init_val;
  }
  return bool_array;
}


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
  int init_val
  ) {
  int* int_array = new int[array_length];
  for (int i = 0; i<array_length; i++) {
    int_array[i] = init_val;
  }
  return int_array;
}


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
  ) {
    
  unsigned long* ulong_array = new unsigned long[array_length];
  for (int i = 0; i<array_length; i++) {
    ulong_array[i] = init_val;
  }
  return ulong_array;
  
}


/*--------------------------------------------------
 * Type: Constant
 * float LOG_BASE_CONSTANT
 *  Constant values used to convert log(number) into
 *    base 256 used for byte conversion in
 *    num_bytes_for_bytestring()
 *--------------------------------------------------
 */
const float LOG_BASE_CONSTANT = 1/log(float(256));

/*--------------------------------------------------
 * Type: Function
 * int num_bytes_for_bytestring(unsigned long)
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
int num_bytes_for_bytestring (unsigned long input_ulong) {
  int num_bytes = 0;
  if (input_ulong == 0 || input_ulong == 1){
    num_bytes = 1;
  }
  else {
    num_bytes = ceil(log(input_ulong)*LOG_BASE_CONSTANT);
    if (num_bytes < 1) {
      num_bytes = 1;
    }
  }
  return num_bytes;
}


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
void parse_ulong_into_bytes(
  unsigned long input_ulong, 
  int num_bytes,
  byte* byte_array
  ){

  unsigned long rem = 0;
  unsigned long num = input_ulong;

  for (int i = 0; i < num_bytes; i++) {
    byte_array[i] = 0x00;
  }

  for (int byte_index = num_bytes - 1; byte_index >= 0; byte_index--) {
    rem = num % 256;
    byte_array[byte_index] = byte(rem);
    num = (num-rem) / 256;
  }
  
}


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
  ) {
    
  int num_bytes = num_bytes_for_bytestring(input_ulong);
  byte byte_array[num_bytes];
  parse_ulong_into_bytes(
    input_ulong, 
    num_bytes,
    byte_array
    );
  if (big_endian) {
    for (int i = 0; i < num_bytes; i++) {
      Serial.write(byte_array[i]);
    }
  }
  else {
    for (int i = num_bytes-1; i >= 0; i--) {
      Serial.write(byte_array[i]);
    }
  }
  
}


/*--------------------------------------------------
 * Type: Constant
 * const unsigned long*
 *  The values of 256^n used for interpreting bytes
 *    as digits in a 4-byte unsigned long. Increases
 *    accuracy and lowers overhead to store as 
 *    constants in an array.
 *--------------------------------------------------
 */
const unsigned long ULONG_BASE_CONSTANTS[] = {
  1,
  256,
  65536,
  16777216,
};


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
  ) {

    unsigned long elapsed = 0;
    if (now_micros < last_micros) {
      // Rollover has occurred!
      elapsed = (42949672955 - last_micros) + now_micros + 1;
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



  
