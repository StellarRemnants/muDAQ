/* Possible UNO BAUD values
0, 50
1, 75
2, 110
3, 134
4, 150
5, 200
6, 300
7, 600
8, 1200
9, 1800
10, 2400
11, 4800
12, 9600
13, 19200
14, 38400
15, 57600
16, 115200
17, 230400
18, 460800
19, 500000
20, 576000
21, 921600
22, 1000000
23, 1152000
24, 1500000
25, 2000000
26, 2500000
27, 3000000
28, 3500000
29, 4000000
 */

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
 const int NUM_ALLOWED_BAUDRATES = 30;
