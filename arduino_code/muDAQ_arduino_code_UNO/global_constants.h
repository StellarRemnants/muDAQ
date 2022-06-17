/*==================================================
 * global_constants.h
 * Created:       2022-05-09
 * Last Modified: 2022-05-22
 * By: Joseph Lewis-Merrill
 * 
 * Description: 
 *    Contains global constants used throughout the 
 *      muDAQ program
 *==================================================
 */

 
#ifndef GLOBAL_CONSTANTS_H_INCLUDED //Prevents redefining values
#define GLOBAL_CONSTANTS_H_INCLUDED


#include <Arduino.h>


/*--------------------------------------------------
 * Type: Constant
 * const unsigned long DEFAULT_BAUDRATE
 *  Sets the baudrate (bits/second) for serial
 *    communication initially used by the Arduino.
 *    This will be the baudrate while the program is
 *    running unless it is changed later. [Variable
 *    baudrate not yet implemented as of 2022-05-20]
 *--------------------------------------------------
 */
const unsigned long DEFAULT_BAUDRATE = 230400;


/*--------------------------------------------------
 * Type: Constant
 * const unsigned long DEFAULT_SERIAL_DELAY
 *  Sets the time the program will delay (in 
 *    milliseconds) when there are no bytes to be
 *    read from serial before checking again. Low
 *    values will respond to commands faster, higher
 *    values will reduce CPU usage.
 *--------------------------------------------------
 */
const unsigned long DEFAULT_SERIAL_DELAY = 1;


/*--------------------------------------------------
 * Type: Constants
 * const byte <Serial Key Bytes>
 *  Each of the following sets what bytes correspond
 *    to what signals for serial communication. 
 *    These must also be changed on the controller
 *    side for communication to function properly.
 *    
 *    DEFAULT_CONNECT_BYTE
 *      -> Expected byte to be received by Arduino
 *          to initiate serial communication.
 *    
 *    DEFAULT_RESTART_BYTE
 *      -> Expected byte to be received by Arduino
 *          to initiate restart process.
 *      
 *    DEFAULT_CONFIRM_BYTE
 *      -> Byte sent to confirm a valid value has
 *          been received.
 *      
 *    DEFAULT_REJECT_BYTE
 *      -> Byte sent to indicate an invalid value 
 *          has been received.
 *    
 *--------------------------------------------------
 */
const byte DEFAULT_CONNECT_BYTE = 0x11;
const byte DEFAULT_RESTART_BYTE = 0xDD;
const byte DEFAULT_CONFIRM_BYTE = 0xEE;
const byte DEFAULT_REJECT_BYTE = 0xFF;


/*--------------------------------------------------
 * Type: Constant
 * const int DEFAULT_RESTART_COUNT
 *  Sets the number of times that the restart byte
 *    must be received via serial to initiate the
 *    restart process. Values greater than 1 allow
 *    for additional protection against accidental
 *    restart but will take longer to process and 
 *    risk some restart bytes being lost to noise.
 *--------------------------------------------------
 */
const int DEFAULT_RESTART_COUNT = 4;


/*--------------------------------------------------
 * Type: Constant
 * const String <Message Key Strings>
 *  String values used to denote parts within data 
 *    messages.
 *    
 *    VAL_SEPARATOR
 *      -> Separates the values within a channel's
 *          data string. Typically a channel's data
 *          string looks like this, for a value
 *          separator value of ",":
 *          
 *          <CH#>,<Time [mus]>,<ADC Val>
 *    
 *    CH_SEPARATOR
 *      -> Separates channel strings from each other
 *          within a message. For a ch. separator
 *          value of ";", with n channels measured,
 *          each message will look like this:
 *        
 *          <CH1 msg>;<CH2 msg>;[...];<CHn msg>
 *    
 *    MSG_TERMINATOR
 *      -> Signifies the end of the message string.
 *          Usually a universal newline to make each
 *          message string compatible with the
 *          "readline" function for most languages.
 *          For a message terminator value of "\r\n"
 *          each message will look like this:
 *          
 *          <CH messages>\r\n
 *          
 *    A typical message for two channels loosk like:
 *    
 *    "\x0e,'\x1fbX,\x00;\x13,'\x1fb\xe0,\x00\r\n"
 *    
 *--------------------------------------------------
 */
const String VAL_SEPARATOR = ",";
const String CH_SEPARATOR = ";";
const String MSG_TERMINATOR = "\r\n";


/*--------------------------------------------------
 * Type: Constants
 * const byte <Valid Pin Count Values>
 *  Set minimum and maximum values allowed for the
 *    number of pins to read from. This sets the
 *    length of the arrays that hold the pin ids,
 *    time of samples, and sample adc values.
 *    
 *    MIN_VALID_PIN_COUNT
 *      -> The minimum number acceptable to specify
 *          the number of pins, as a byte. Default 
 *          is 1 (0x01).
 *    
 *    MAX_VALID_PIN_COUNT
 *      -> The maximum number acceptable to specify
 *          the number of pins, as a byte. Default
 *          is 255 (0xFF).
 *    
 *--------------------------------------------------
 */
const byte MIN_VALID_PIN_COUNT = 0x01;
const byte MAX_VALID_PIN_COUNT = 0xFF;


/*--------------------------------------------------
 * Type: Constant
 * const int VALID_PINS[]
 *  Sets the values corresponding to the allowed
 *    pin ids, the integers which uniquely identify
 *    the pins on the arduino board. These can
 *    commonly be given by built-in constants like:
 *    
 *    A0, A1, A2, etc. for the Arduino Uno
 *    A11, A12, A33, etc. for the Artemis ATP
 *    
 *    They can alternatively be specified directly 
 *    as integers, like:
 *    
 *    14, 15, 16, etc. for the Arduino Uno
 *    11, 12, 33, etc. for the Artemis ATP
 *    
 *    The former method will throw compiler errors
 *    when trying to compile for different boards,
 *    the latter method may obfuscate which pin
 *    corresponds to which value.
 *--------------------------------------------------
 */
const int VALID_PINS[] = {
    // Uno pins
    A0, A1, A2, A3, A4, A5

    // ATP PINS
    //A11, A12, A13, A16, A29, A31, A32, A33, A34, A35
};


/*--------------------------------------------------
 * Type: Constant
 * const int NUM_VALID_PINS
 *  Sets the length of the array VALID_PINS for use
 *    in checking the validity of pin ids. This 
 *    value is autocalculated and shouldn't need to 
 *    be modified.
 *--------------------------------------------------
 */
const int NUM_VALID_PINS = (int)(sizeof(VALID_PINS)/sizeof(VALID_PINS[0]));





#endif
