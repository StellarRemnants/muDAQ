/*
Global Constants
 */

#include "initialization_fncs.h"

//const unsigned long BAUD = 115200;
const unsigned long BAUD = 230400;
const int DELAY = 0;
const int RESOLUTION = 14; // 10 for Uno, 14 for ATP

/*
Variable Initialization
 */
int num_pins = 0;
int *pin_array;
int *read_vals;
unsigned long *read_times;

bool restart_signal = 1;

void setup() {
  restart_signal = 0;
  Serial.begin(BAUD); 
  pinMode(LED_BUILTIN, OUTPUT);
  analogReadResolution(RESOLUTION);
  digitalWrite(LED_BUILTIN, LOW);

  bool initial_loop = 1;

  while (initial_loop == 1) {
    digitalWrite(LED_BUILTIN, HIGH);
    if (Serial.available() > 0) {
      on_init_serial(initial_loop, DELAY, pin_array, num_pins, read_vals, read_times);
    }
    digitalWrite(LED_BUILTIN, LOW);
    delay(DELAY);
  }
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);

  if (Serial.available() > 0) {
    restart_signal = check_for_restart_signal();
  }
  if (restart_signal == 1) {
    setup();
  }
  
  get_read_vals(pin_array, read_vals, num_pins, read_times);
  serial_print_read_vals(read_vals, read_times, num_pins);
  digitalWrite(LED_BUILTIN, LOW);
}
