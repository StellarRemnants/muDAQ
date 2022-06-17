/*==================================================
 * initialization_fncs.cpp
 * Created:       2022-05-09
 * Last Modified: 2022-05-22
 * By: Joseph Lewis-Merrill
 * 
 * Description:
 *    Contains low-level functions for initializing 
 *      the muDAQ program. Called by higher-level 
 *      functions in primary_fncs.cpp
 *==================================================
 */


#include <Arduino.h>
#include "base_fncs.h"
#include "global_constants.h"


/*--------------------------------------------------
 * Type: Function
 * void begin_serial([unsigned long])
 *  Initializes the serial connection to the 
 *    specified baudrate. Higher baudrates allow
 *    faster communication between devices, and thus
 *    a higher sample rate in principle, but also 
 *    incurs a higher CPU usage and diminishing
 *    returns on efficiency.
 *  
 *  Arguments:
 *    unsigned long baudrate 
 *      -> The baudrate in bits/second.
 *    
 *  Returns
 *    None
 *--------------------------------------------------
 */
void begin_serial(unsigned long baudrate=DEFAULT_BAUDRATE) {
  Serial.begin(baudrate);
}

/*--------------------------------------------------
 * Type: Function
 * void wait_for_serial(int)
 *  Waits until there is at least one byte to be
 *    read from the serial input buffer, delaying
 *    in spans of delay_duration milliseconds.
 *    Will hang forever if no bytes are received.
 *  
 *  Arguments:
 *    int delay_duration 
 *      -> Time to between read attempts, in ms
 *    
 *  Returns
 *    None
 *--------------------------------------------------
 */
void wait_for_serial(int delay_duration) {
  while (Serial.available() == 0) {
    delay(delay_duration);
  }
}


/*--------------------------------------------------
 * Type: Function
 * void wait_for_specific_byte(byte[, byte, byte, unsigned long])
 *  Waits to receive expected_byte over serial, 
 *    responding with confirm_byte when the expected
 *    byte is received and with reject_byte when any
 *    other byte is received. Delays serial_delay ms
 *    after reads of incorrect bytes. Will hang
 *    indefinitely if the correct byte is never
 *    received.
 *  
 *  Arguments:
 *    byte expected_byte
 *      -> The byte expected to be received.
 *    
 *    byte confirm_byte
 *      -> The byte sent when the expected byte has
 *          been received.
 *    
 *    byte reject_byte
 *      -> The byte sent when any byte other than
 *          the expected byte has been received.
 *    
 *    unsigned long serial_delay
 *      -> Time (in ms) to wait after a rejection
 *          has been sent.
 *    
 *  Returns
 *    None
 *--------------------------------------------------
 */
void wait_for_specific_byte(
  byte expected_byte, 
  byte confirm_byte = DEFAULT_CONFIRM_BYTE, 
  byte reject_byte = DEFAULT_REJECT_BYTE,
  unsigned long serial_delay = DEFAULT_SERIAL_DELAY
  ) {
    
  byte read_byte = 0;
  while (true) {
    wait_for_serial(serial_delay);
    read_byte = Serial.read();
    if (read_byte == expected_byte) {
      Serial.write(confirm_byte);
      break;
    }
    else {
      Serial.write(reject_byte);
    }
  }
  
}


/*--------------------------------------------------
 * Type: Function
 * byte wait_for_byte_in_range(byte, byte[, bool, byte, byte, unsigned long])
 *  Wait to receive a byte over serial which is 
 *    between the two values given. End inclusivity 
 *    may be toggled. Will hang indefinitely unless
 *    a byte within the given range is received.
 *  
 *  Arguments:
 *    byte low_byte
 *      -> The lower end of the allowed range. If
 *          end_inclusive, includes this value.
 *      
 *    byte high_byte
 *      -> The upper end of the allowed range. If
 *          end_inclusive, includes this value.
 *          
 *    bool end_inclusive
 *      -> Toggles whether the endpoints of the
 *          range are included as valid.
 *    
 *    byte confirm_byte
 *      -> The byte sent when the expected byte has
 *          been received.
 *    
 *    byte reject_byte
 *      -> The byte sent when any byte other than
 *          the expected byte has been received.
 *    
 *    unsigned long serial_delay
 *      -> Time (in ms) to wait after a rejection
 *          has been sent.
 *    
 *  Returns
 *    byte
 *      -> The first byte received which is within
 *          the specified range.
 *--------------------------------------------------
 */
byte wait_for_byte_in_range(
  byte low_byte, 
  byte high_byte, 
  bool end_inclusive=true,
  byte confirm_byte = DEFAULT_CONFIRM_BYTE, 
  byte reject_byte = DEFAULT_REJECT_BYTE,
  unsigned long serial_delay = DEFAULT_SERIAL_DELAY
  ) {

  byte read_byte = 0;
  bool byte_valid = false;
  while (true) {
    wait_for_serial(serial_delay);
    read_byte = Serial.read();
    
    if (end_inclusive) {
      byte_valid = byte_in_range_incl(read_byte, low_byte, high_byte);
    }
    else {
      byte_valid = byte_in_range_excl(read_byte, low_byte, high_byte);
    }
    
    if (byte_valid) {
      Serial.write(confirm_byte);
      return read_byte;
    }
    else {
      Serial.write(reject_byte);
    }
  }
  
}


/*--------------------------------------------------
 * Type: Function
 * int get_single_pin_val([int, const int*, unsigned long, byte, btye])
 *  Reads bytes from serial until one corresponding 
 *    to a valid pin is received. For each invalid 
 *    byte, sends a rejection. Sends a single 
 *    confirmation when a valid byte is received.
 *  
 *  Arguments:
 *    int num_valid_pins
 *      -> Length of the array pointed to by
 *          valid_pin_array.
 *      
 *    const int* valid_pin_array  
 *      -> Array of integers representing the pin 
 *          ids which correspond to valid pins for
 *          analogRead on the board in use. See
 *          VALID_PINS[] in global_constants.h
 *    
 *    unsigned long serial_delay
 *      -> Time (in ms) to wait after a rejection
 *          has been sent.
 *    
 *    byte confirm_byte
 *      -> The byte sent when the expected byte has
 *          been received.
 *    
 *    byte reject_byte
 *      -> The byte sent when any byte other than
 *          the expected byte has been received.
 *    
 *  Returns
 *    TEMPLATE
 *--------------------------------------------------
 */
int get_single_pin_val(
  int num_valid_pins = NUM_VALID_PINS,
  const int* valid_pin_array = VALID_PINS,
  unsigned long serial_delay = DEFAULT_SERIAL_DELAY,
  byte confirm_byte = DEFAULT_CONFIRM_BYTE, 
  byte reject_byte = DEFAULT_REJECT_BYTE
  ) {
  
  int read_int = 0;
  byte read_byte = 0x00;
  while (true) {
    wait_for_serial(serial_delay);
    read_byte = Serial.read();
    read_int = (int)(read_byte);
    if (int_in_array(
          read_int,
          num_valid_pins,
          valid_pin_array
          )
       ) {
        Serial.write(confirm_byte);
        return read_int;
    }
    else {
      Serial.write(reject_byte);
    }
  }
}
