Installation
============

The project is developed on MacOS Monterey (12.6) using python 3.10.8. External python
packages are:

- :mod:`astropy` 5.1.1_0
- :mod:`numpy` 1.23.4_0
- :mod:`pyserial` 3.5.0
- :mod:`requests` 2.28.1
- :mod:`zmq` 24.0.1_0

Additionally, there is a fake arduino server that uses the :mod:`socat` utility for
creating virtual sockets that can mimic the serial port.

- :mod:`socat` 1.7.4.3_0

The following steps installs everything into a virtualenv::

   > virtualenv pushto
   > cd pushto
   > source bin/activate
   > pip install git+https://github.com/ptoale/pushto.git

