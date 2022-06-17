bool validate_pin(int pn);

void wait_for_serial(int delay_duration);

void serial_print_pin_array(int* pin_array, int num_pins);

void serial_print_read_vals(int *read_vals, unsigned long *read_times, int num_pins);

bool check_for_restart_signal();

int* initialize_pin_array(int num_pins);

int* initialize_read_vals(int num_pins);

unsigned long* initialize_read_times(int num_pins);

void get_read_vals(int *pin_array, int *read_vals, int num_pins, unsigned long *read_times);

bool on_valid_init_byte(bool &initial_loop, int delay_duration, 
    int *&pin_array, int &num_pins, int *&read_vals, unsigned long *&read_times);

bool on_init_serial(bool &initial_loop, int delay_duration, 
    int *&pin_array, int &num_pins, int *&read_vals, unsigned long *&read_times);
