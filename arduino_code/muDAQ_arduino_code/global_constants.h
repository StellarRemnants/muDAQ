/*
 * TEMPLATE
 * Created:       2022-05-09
 * Last Modified: 2022-05-10
 * By: Joseph Lewis-Merrill
 * 
 * Description: 
 *    Contains global constants used throughout the muDAQ program
 */
#ifndef GLOBAL_CONSTANTS_H_INCLUDED
#define GLOBAL_CONSTANTS_H_INCLUDED

#include <Arduino.h>

const unsigned long DEFAULT_BAUDRATE = 230400;
const unsigned long DEFAULT_SERIAL_DELAY = 1;

const byte DEFAULT_CONNECT_BYTE = 0x11;
const byte DEFAULT_RESTART_BYTE = 0xDD;
const byte DEFAULT_CONFIRM_BYTE = 0xEE;
const byte DEFAULT_REJECT_BYTE = 0xFF;

const int DEFAULT_RESTART_COUNT = 4;

const int READ_RESOLUTION = 10;

const String VAL_SEPARATOR = ",";
const String CH_SEPARATOR = ";";
const String MSG_TERMINATOR = "\r\n";

const byte MIN_VALID_PIN_COUNT = 0x01;
const byte MAX_VALID_PIN_COUNT = 0xFF;

int VALID_PINS[] = {
//  A0, A1, A2, A3, A4, A5
    33,
};
const int NUM_VALID_PINS = (int)(sizeof(VALID_PINS)/sizeof(VALID_PINS[0]));

const int NUM_ALLOWED_BAUDRATES = 30;
const unsigned long ALLOWED_BAUDRATES[] = {
50,
75,
110,
134,
150,
200,
300,
600,
1200,
1800,
2400,
4800,
9600,
19200,
38400,
57600,
115200,
230400,
460800,
500000,
576000,
921600,
1000000,
1152000,
1500000,
2000000,
2500000,
3000000,
3500000,
4000000
};









#endif
