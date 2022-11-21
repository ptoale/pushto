Scripts
===============

There are several included scripts:

- pushto
- moni_listener
- fake_arduino
- check_encoders
- check_stellarium

The main user interface is invoked with::

    > pushto [-h] [--config_file CONFIG_FILE]

The pointing/alignment data stream can be subscribed to with::

   > moni_listener [-h] host port

The :class:`fake_arduino` service mimics serial communication via a virtual socket. To use it,
first create the virtual sockets (requires the :mod:`socat` utility)::

   > socat -dd pty,raw,echo=0 pty,raw,echo=0,ispeed=9600,ospeed=9600

Record the two ports that are recorded: one is written to and the other is read by
:class:`pushto.telescope.Telescope`. You can put socat in the background with::

   > ^Z
   > bg

Then start the faux server with::

   > fake_arduino [-h] <port1>

This too can be put in the background. At this point <port2> will contain serial data
of the correct format but with very little content.

The :class:`pushto.telescope.Telescope` class can be exercised without the rest
of the code with::

    > check_encoders [-h] [--port PORT] [-d]

This will read the serial port and print out the corresponding telescope attitude.

The last script is useful for checking the difference between Stellarium and
:mod:`astropy`. Make sure Stellarium is running and the telescope is connecting, then::

    > check_stellarium

From within Stellarium, select an object, click `Current object`, and then click `Slew`.