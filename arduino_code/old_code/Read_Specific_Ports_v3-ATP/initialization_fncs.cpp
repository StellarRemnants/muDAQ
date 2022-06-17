#include <Arduino.h>
/*
 * Module Constants
 */

 
const bool TRUE = 1, True = 1;
const bool FALSE = 0, False = 0;

const int UNO = 1;
const int ATP = 2;


const int UNO_VALID_PINS[] = { // UNO analog pin designations
//A0, A1, A2, A3, A4, A5
};
const int ATP_VALID_PINS[] = { // Artemis ATP analog pin designations
A29, A11, A34, A33, A16, A31, 
A13, A12, A32, A35,
};

const int DEVICE = ATP;           // Select device (Used to determine valid pin ranges)
const int CONFIRMATION_BYTE = 1;  // Value that must be received over Serial to begin initialization
const int RESTART_VAL = 42;       // Value that must be received over serial to begin restart process
const int RESTART_COUNT = 4;      // Number of times <RESTART_VAL> must be received to confirm restart

/*
 * Validation Functions
 */
bool validate_pin(int pn) {
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  // bool validate_pin(int pn)
  //
  // Check whether pn is a valid analog pin according to DEVICE (const int) and the
  //   corresponding VALID_PINS array
  //
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  
  const int *valid_pins;
  int num_valid_pins; 
  
  if (DEVICE == UNO) {
    valid_pins = UNO_VALID_PINS;
    num_valid_pins = (int)(sizeof(UNO_VALID_PINS)/sizeof(UNO_VALID_PINS[0]));
  }
  else if (DEVICE == ATP) {
    valid_pins = ATP_VALID_PINS;
    num_valid_pins = (int)(sizeof(ATP_VALID_PINS)/sizeof(ATP_VALID_PINS[0]));
  }
  else {
    valid_pins = UNO_VALID_PINS;
    num_valid_pins = (int)(sizeof(UNO_VALID_PINS)/sizeof(UNO_VALID_PINS[0]));
  }
  
  bool found_in_list = False;
  for (int i=0; i<num_valid_pins; i++) {
    if (pn == valid_pins[i]) {
      found_in_list = True;
      break;
    }
  }
  return found_in_list;
}

/*
 * Serial Utility Functions
 */
void wait_for_serial(int delay_duration) {
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  // void wait_for_serial(int delay_duration)
  //
  // Delay execution in steps of <delay_duration> milliseconds until 
  //   Serial.available() > 0 (i.e. until there is something in the Serial input buffer)
  //
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  
  while (Serial.available() == 0) {
    delay(delay_duration);             // Wait until Serial sends number of pins to read
  }
}

void serial_print_pin_array(int *pin_array, int num_pins) {
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  // void serial_print_pin_array(int *pin_array, int num_pins)
  //
  // Pretty (human legibly) print the contents of pin_array to the Serial output buffer
  //   Useful for externally confirming the pins have been set correctly
  //
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  
  Serial.print("pin_array: ");
  for (int i=0; i<num_pins; i++) {
    Serial.print(pin_array[i]);
    Serial.print(",");
  }
  Serial.println("");
}

void serial_print_read_vals(int *read_vals, unsigned long *read_times, int num_pins) {
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  // void serial_print_read_vals(int *read_vals, unsigned long *read_times, int num_pins)
  //
  // Print read_vals and read_times to the Serial output buffer. Values are written as
  //   hexadecimal values with separation characters. Each line (message) is broken into
  //   sections by corresponding pin (words). The format is as follows:
  //     
  //     <time CH0>,<ADC CH0>;<t_delta CH1>,<ADC CH1>;<t_delta CH2>,<ADC CH2>;[...]
  //   
  //   where:
  //     - CHn represents analog channel n, starting at 0
  //     - <time CH0> is the timetamp of CH0 in microseconds since program start
  //     - <ADC CHn> is the ADC int returned for CHn
  //     - <t_delta CHn> is the delay in microseconds between the CH0 and CHn measurements
  //   
  //   A valid word is two HEX values separated by a comma ","
  //   A valid message is composed of one or more words, each followed by a semicolon ";"
  //
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  
  unsigned long follow_time = 0;
  //Serial.print("read_vals: ");
  for (int i=0; i<num_pins; i++) {
    if (i==0){
      Serial.print(read_times[0], HEX);
    }
    else {
      follow_time = read_times[i] - read_times[0];
      Serial.print(follow_time, HEX);
    }
    Serial.print(",");
    Serial.print(read_vals[i], HEX);
    Serial.print(";");
  }
  Serial.println("");
}

bool check_for_restart_signal() {
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  // bool check_for_restart_signal()
  //
  // Triggered by a byte received over Serial while in the main loop read
  //   If the received byte is <RESTART_VAL>, reply with <RESTART_VAL>
  //   Serial must send <RESTART_VAL> <RESTART_COUNT> times to confirm restart.
  //   Reception of any other byte will cancel the restart and resume data collection.
  //
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  
  int serial_read_byte = 0;
  int wait_delay = 1;
  bool restart = True;
  for (int i = 0; i < RESTART_COUNT; i++) {
    serial_read_byte = Serial.read();
    if (serial_read_byte == RESTART_VAL) {
      Serial.write(RESTART_VAL);
      wait_for_serial(wait_delay);
    }
    else {
      restart = False;
      break;
    }
  }
  return restart;
}

/*
 * Array Initialization Functions
 */
int* initialize_pin_array(int num_pins) {
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  // int* initialize_pin_array(int num_pins)
  //
  // Create a new int array with length <num_pins> and return a pointer to the new
  //   array. Functionally identical to <initialize_read_vals>
  //
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  
  int *pin_array = new int[num_pins];
  for (int i=0; i<num_pins; i++) {
    *(pin_array+i) = 0;
  }
  return pin_array;
}

int* initialize_read_vals(int num_pins) {
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  // int* initialize_read_vals(int num_pins)
  //
  // Create a new int array with length <num_pins> and return a pointer to the new
  //   array. Functionally identical to <initialize_pin_array>
  //
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  
  int *read_vals = new int[num_pins];
  for (int i=0; i<num_pins; i++) {
    *(read_vals+i) = 0;
  }
  return read_vals;
}

unsigned long* initialize_read_times(int num_pins) {
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  // unsigned long* initialize_read_times(int num_pins)
  //
  // Create a new unsigned long array with length <num_pins> and return a pointer 
  //   to the new array. 
  //
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  
  unsigned long *read_times = new unsigned long[num_pins];
  for (int i=0; i<num_pins; i++) {
    *(read_times+i) = 0;
  }
  return read_times;
}

/*
 * Get Data <- Most important Fnc for data collection
 */
void get_read_vals(int *pin_array, int *read_vals, int num_pins, unsigned long *read_times) {
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  // void get_read_vals(int *pin_array, int *read_vals, 
  //   int num_pins, unsigned long *read_times)
  //
  // Reads ADC values for the pins given in <pin_array> and writes the read value to
  //   <read_vals>. Also writes the corresponding timestamps to <read_times>
  //
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  
  for (int i=0; i<num_pins; i++) {
    read_vals[i] = analogRead(pin_array[i]);
    read_times[i] = micros();
  }
}

/*
 * Initialization on valid initial byte from Serial
 */
bool on_valid_init_byte(bool &initial_loop, int delay_duration, int *&pin_array, 
  int &num_pins, int *&read_vals, unsigned long *&read_times) {
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  // bool on_valid_init_byte(bool &initial_loop, int delay_duration, int *&pin_array, 
  //   int &num_pins, int *&read_vals, unsigned long *&read_times)
  //
  // Begins the initialization process once a valid intial byte has been received.
  //   Waits to receive a byte specifying number of pins to be read and creates arrays
  //   with the appropriate lengths. Then sends <num_pins> to confirm creation.
  // Thereafter, waits to received bytes specifying pin identities and validates said
  //   values. Returns 0xFE (255) for invalid pin assignments. Otherwise, returns the
  //   received byte to confirm selection.
  //
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  
  Serial.write(byte(0x0));            // Respond 0x00 to indicate succesful contact
  
  wait_for_serial(delay_duration);
  int serial_read_byte = Serial.read();
  num_pins = serial_read_byte;
  
  pin_array = initialize_pin_array(num_pins);
  read_vals = initialize_read_vals(num_pins);
  read_times =  initialize_read_times(num_pins);

  Serial.write(num_pins);     // Respond with num_pins to validate creation of pin array
  int pin_number = 0;
  for (int i=0; i<num_pins; i++) { // Read in pins to be read from
    bool valid_pin = False;

    while (!valid_pin) {
      wait_for_serial(delay_duration);
      serial_read_byte = Serial.read();
      pin_number = serial_read_byte;
      valid_pin = validate_pin(pin_number);

      if (!valid_pin) {
        Serial.write(254); // Respond 0xFE for invalid pin
      }
    }

    *(pin_array+i) = pin_number;
    Serial.write(pin_number);
  }
//  serial_print_pin_array();
  initial_loop = False;
  return initial_loop;
}

/*
 * On serial available to read
 */
bool on_init_serial(bool &initial_loop, int delay_duration, int *&pin_array, 
  int &num_pins, int *&read_vals, unsigned long *&read_times) {
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  // bool on_init_serial(bool &initial_loop, int delay_duration, int *&pin_array, 
  //   int &num_pins, int *&read_vals, unsigned long *&read_times)
  //
  // Called once a byte has been received. If byte is <CONFIRMATION_BYTE>, begin 
  //   intialization process. Otherwise, respond 0xFF (255) to indicate sync failure.
  //   Used to prevent accident start of initialization process.
  //
  //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%//
  
  int serial_read_byte = Serial.read();
      
  //Received a valid initialization byte
  
  if (serial_read_byte == CONFIRMATION_BYTE) { 
    initial_loop = on_valid_init_byte(initial_loop, delay_duration, pin_array, num_pins, read_vals, read_times);
  } // if serial_read_byte == 1
  
  // Received an invalid initialization byte
  else {
    Serial.write(255);          // Respond 0xFF for sync failure
  }

  return initial_loop;
}
