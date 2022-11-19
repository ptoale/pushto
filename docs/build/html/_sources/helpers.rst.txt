Helper Programs
===============

There are two standalone programs in the `utils` directory that may be of help. The first is 
a fake arduino server that can mimic serial communication via a virtual socket. To use it, 
first create the virtual sockets (requires to socat utility)::

   > socat -dd pty,raw,echo=0 pty,raw,echo=0,ispeed=9600,ospeed=9600

Record the two ports that are recorded: one is written to and the other is read by
:class:`pushto.arduino.ArduinoProxy`. You can put socat in the background with::

   > ^Z

and then::

   > bg

Then start the faux server with::

   > python fake_arduino.py <port1>

This too can be put in the background. At this point <port2> will contain serial data
of the correct format but with very little content.

The other help is a subscriber service for the monitoring stream. You must first start the system
with a configured monitoring PUB address and then run::

   > python moni_listener.py <moni_host> <moni_port>
   
