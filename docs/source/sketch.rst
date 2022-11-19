Arduino Sketch
==============

The arduino sketch makes use of the :mod:`QuadratureEncoder` library to
read the attached encoders on interrupt. The library makes available

- the current encoder count
- the current encoder error count

for up to four encoders. The sketch sets up the serial communication and
the :obj:`Encoders` objects, and then writes the encoder data to the serial
port every 50 ms. The data is written as a string consisting of space-separated
fields and terminated with '\\r\\n'. The fields are

- time: most recent :func:`millis()` call
- encoder1_count: most recent count on encoder 1
- encoder2_count: most recent count on encoder 2
- encoder1_error_count: most recent error count on encoder 1
- encoder2_error_count: most recent error count on encoder 2

The smallest message is 5 zeros which has a size of 11 B; the typical size is 25 B. 
The 50 ms reporting will result in about 4 kb/s which should be easily 
supported by a baud rate of 9600.
