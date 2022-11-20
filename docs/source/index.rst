PushTo Documentation
==================================

The software side of my push-to digital setting circles project
is documented here. And by software, I mean the python package that
allows for display of telescope pointing in the Stellarium open-source
planetarium application, based on data from rotary encoders attached
to both the altitude and the azimuth bearings. The goal is to achieve
5 arcmin pointing resolution.

The encoders are readout by an Arduino Uno, which writes data to the
serial port. The Stellarium Telescope Control (STC) plugin accepts telescope
coordinates in J2000 right ascension and declination. The main job of this
package is to read encoder data on the serial port, translate it into equatorial
coordinates, and to communicate those coordinates the STC.

The main classes include proxies for both the serial port connection to
the arduino and the socket connection to the STC.
The control module is responsible for communication with both proxy classes,
managing alignment data, and translating between 3 coordinate systems.

1. the telescope attitude
2. the local horizontal Alt-Az system
3. the J2000 equatorial RA-Dec system

Step 2 requires telescope alignment with at least 2 stars. The STC can send
slew commands to a telescope, consisting of the coordinates of a selected
object. The slew command currently must be initiated from within Stellarium
by clicking on buttons. The Stellarium Remote Control (SRC) rpc api does allow
for some remote execution and perhaps we could trigger alignment data internally.
The remaining modules handle interfacing with the :mod:`astropy` package, handling
configuration data, and proving a menu-driven text-based user interface.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   installation
   coords
   code
   scripts
   sketch


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
