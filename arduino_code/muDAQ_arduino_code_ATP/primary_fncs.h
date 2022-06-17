/*==================================================
 * TEMPLATE
 * Created:       2022-05-09
 * Last Modified: 2022-05-22
 * By: Joseph Lewis-Merrill
 * 
 * Description: 
 *    Contains declarations for functions in 
 *      primary_fncs.cpp
 *==================================================
 */


#include "global_constants.h"


/*--------------------------------------------------
 * Type: Function
 * struct daq_settings setup_loop()
 *  Initializes the muDAQ program based on input 
 *    from the serial controller program. Returns a
 *    struct which contains the program settings and
 *    data arrays. See struct daq_settings under
 *    base_fncs.h for morer information on the 
 *    struct. 
 *  
 *  Arguments:
 *    None
 *    
 *  Returns
 *    struct daq_settings ret_settings
 *      -> Struct containing program settings and 
 *          data arrays for program.
 *--------------------------------------------------
 */
struct daq_settings setup_loop();


/*--------------------------------------------------
 * Type: Function
 * bool main_loop(struct daq_settings*)
 *  Data collection loop run after initialization
 *    is completed. First checks whether a restart
 *    has been requested. If not, runs 
 *    read_and_write_adc(), which reads each pin 
 *    that has not been read for at least its 
 *    corresponding pin delay and then reports the
 *    read values via serial.
 *  
 *  Arguments:
 *    struct daq_settings* global_daq_settings 
 *      -> Pointer to the global daq_settings struct
 *          which allows modification of its values
 *          by subfunctions.
 *    
 *  Returns
 *    bool
 *      -> true:  Restart requested
 *      -> false: No restart requested
 *--------------------------------------------------
 */
bool main_loop(struct daq_settings* global_daq_settings);
