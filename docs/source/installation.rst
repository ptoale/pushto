Installation
============

You are on currently on your own here. I am working on a simple git/pip procedure 
and will update this when appropriate.
The system was/is developed on MacOS Monterey (12.6) using python 3.10.8. The external
python packages that are required are:

- :mod:`numpy` 1.23.4_0
- serial 3.5.0
- zmq 24.0.1_0
- astropy 5.1.1_0

Additionally, there is a fake arduino server that uses the :mod:`socat` utility for
creating virtual sockets that can mimic the serial port.

- socat 1.7.4.3_0

