Scripts
===============

There are several included scripts, including the main user interface:

- pushto
- moni_listener
- fake_arduino
- check_encoders
- check_stellarium


The :class:`fake_arduino` service mimics serial communication via a virtual socket. To use it,
first create the virtual sockets (requires the :mod:`socat` utility)::

   > socat -dd pty,raw,echo=0 pty,raw,echo=0,ispeed=9600,ospeed=9600

Record the two ports that are recorded: one is written to and the other is read by
:class:`pushto.telescope.Telescope`. You can put socat in the background with::

   > ^Z

and then::

   > bg

Then start the faux server with::

   > python fake_arduino.py <port1>

This too can be put in the background. At this point <port2> will contain serial data
of the correct format but with very little content.

The :class:`moni_listener` subscribes to the pointing data stream. To use it::

   > python moni_listener.py <moni_host> <moni_port>

