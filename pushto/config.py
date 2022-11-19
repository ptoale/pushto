#!/usr/bin/env python
"""
Configuration stuff

[COMMUNICATION]
    - host_ip:      computer IP address, can be 127.0.0.1
    - serial_port:  serial port to which the Arduino is connected to
    - stc_port:     port on which the Telescope Control is attached to
    - td_ta_port:   port on which the TD telescope attitudes are published
    - td_eq_port:   port on which the TD equatorial coords are published
    - pd_eq_port:   port on which the PD equatorial coords ars published
    - pd_ta_port:   port on which the pointing model pairs are published

[LOCATION]
    - latitude:     latitude as decimal degree
    - longitude:    longitude as decimal degree, negative for west
    - elevation:    elevation in meters
    - pressure:     pressure in hPa, used for refraction correction
    - temperature:  temperature in C, used for refraction correction
    - rel_humidity: relative humidity [0:1], used for refraction correction

[ENCODERS]
    - theta_npr:    number of counts per revolution for polar encoder, including gearing
    - phi_npr:      number of counts per revolution for azimuthal encoder, including gearing
    - flip_theta:   flip the sense of the polar encoder if true
    - flip_phi:     flip the sense of the azimuthal encoder if true

[POINTING]
    - ia:           index error in azimuth
    - ie:           index error in elevation
    - an:           north-south misalignment of azimuth axis
    - aw:           west-east misalignment of azimuth axis
    - ca:           non-perpendicularity of optical axis and elevation axis
    - npae:         non-perpendicularity of elevation axis and azimuth axis
    - tx:           tube flexure term proportional to cot(el)
    - tf:           tube flexure term proportional to cos(el)

"""
import os
import logging
from configparser import ConfigParser
import importlib.resources
#
import astropy.units as u
from astropy.coordinates import EarthLocation, Latitude, Longitude

#DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'pushto_default.cfg')
DEFAULT_CONFIG_FILE = importlib.resources.read_text(__package__, 'pushto_default.cfg')

class Configuration(object):
    """
    The configuration handler.
    
    :param filename: configuration file name, or None for default configuration
    :type filename: str
    
    """

    def __init__(self, filename=None):
        self.config = ConfigParser()

        fn = DEFAULT_CONFIG_FILE if filename is None else filename
        try:
            self.config.read_file(open(fn))
            logging.info('opened config from %s' % fn)
        except FileNotFoundError as e:
            logging.error(str(e))
            
    def save(self, filename=None):

        fn = DEFAULT_CONFIG_FILE if filename is None else filename

        self.config.write(open(fn, 'w'))        

    """
    Communication info
    """
    def get_host_ip(self):
        """
        Get the host ip address
        
        >>> cfg = Configuration()
        >>> cfg.get_host_ip()
        '127.0.0.1'
        """
        return self.config['COMMUNICATION']['host_ip']
        
    def set_host_ip(self, value):
        """
        Set the host ip address
        
        >>> cfg = Configuration()
        >>> cfg.set_host_ip('127.0.0.1')
        """
        logging.debug('setting host_ip to %s' % str(value))
        self.config['COMMUNICATION']['host_ip'] =  value

    def get_serial_port(self):
        """
        Get the serial port
        
        >>> cfg = Configuration()
        >>> cfg.get_serial_port()
        '/dev/cu.usbmodem143301'
        """
        return self.config['COMMUNICATION']['serial_port']
        
    def set_serial_port(self, value):
        """
        Set the serial port
        
        >>> cfg = Configuration()
        >>> cfg.set_serial_port('/dev/cu.usbmodem143301')
        """
        logging.debug('setting serial port to %s' % value)
        self.config['COMMUNICATION']['serial_port'] = value

    def get_stc_port(self):
        """
        Get the STC port number as an int
        
        >>> cfg = Configuration()
        >>> cfg.get_stc_port()
        10002
        """
        return self.config['COMMUNICATION'].getint('stc_port')
        
    def set_stc_port(self, value):
        """
        Set the STC port number
        
        >>> cfg = Configuration()
        >>> cfg.set_stc_port(10002)
        """
        logging.debug('setting STC port to %s' % str(value))
        self.config['COMMUNICATION']['stc_port'] = str(value)

    def get_td_ta_port(self):
        """
        Get the telescope data: telescope attitude port
        
        >>> cfg = Configuration()
        >>> cfg.get_td_ta_port()
        '10011'
        """
        return self.config['COMMUNICATION']['td_ta_port']
        
    def set_td_ta_port(self, value):
        """
        Set the telescope data: telescope attitude port
        
        >>> cfg = Configuration()
        >>> cfg.set_td_ta_port('10011')
        """
        logging.debug('setting TD-TA port to %s' % value)
        self.config['COMMUNICATION']['td_ta_port'] = value

    def get_td_eq_port(self):
        """
        Get the telescope data: equitorial port
        
        >>> cfg = Configuration()
        >>> cfg.get_td_eq_port()
        '10012'
        """
        return self.config['COMMUNICATION']['td_eq_port']
        
    def set_td_eq_port(self, value):
        """
        Set the telescope data: equatorial port
        
        >>> cfg = Configuration()
        >>> cfg.set_td_eq_port('10012')
        """
        logging.debug('setting TD-EQ port to %s' % value)
        self.config['COMMUNICATION']['td_eq_port'] = value

    def get_pd_eq_port(self):
        """
        Get the pointing data: equatorial port
        
        >>> cfg = Configuration()
        >>> cfg.get_pd_eq_port()
        '10013'
        """
        return self.config['COMMUNICATION']['pd_eq_port']
        
    def set_pd_eq_port(self, value):
        """
        Set the pointing data: equatorial port
        
        >>> cfg = Configuration()
        >>> cfg.set_pd_eq_port('10013')
        """
        logging.debug('setting PD-EQ port to %s' % value)
        self.config['COMMUNICATION']['pd_eq_port'] = value

    def get_pd_ta_port(self):
        """
        Get the pointing data: telescope attitude port
        
        >>> cfg = Configuration()
        >>> cfg.get_pd_ta_port()
        '10014'
        """
        return self.config['COMMUNICATION']['pd_ta_port']
        
    def set_pd_ta_port(self, value):
        """
        Set the pointing data: telescope attitude port
        
        >>> cfg = Configuration()
        >>> cfg.set_pd_ta_port('10014')
        """
        logging.debug('setting PD-TA port to %s' % value)
        self.config['COMMUNICATION']['pd_ta_port'] = value


    """
    Location info
    """
    def get_latitude(self):
        """
        Get the location latitude as an astropy Latitude object
        
        >>> cfg = Configuration()
        >>> cfg.get_latitude()
        <Latitude 33.30167 deg>
        """
        lat = self.config['LOCATION'].getfloat('latitude')
        return Latitude(lat, unit='deg')
        
    def set_latitude(self, latitude):
        """
        Set the location latitude from an astropy Latitude object
        
        >>> cfg = Configuration()
        >>> lat = Latitude(33.30167*u.deg)
        >>> cfg.set_latitude(lat)
        """
        logging.debug('setting latitude to %s' % str(latitude))
        self.config.set('LOCATION', 'latitude', str(latitude.to_value()))   

    def get_longitude(self):
        """
        Get the location longitude as an astropy Longitude object

        >>> cfg = Configuration()
        >>> cfg.get_longitude()
        <Longitude 272.3925 deg>
        """
        lon = self.config['LOCATION'].getfloat('longitude')
        return Longitude(lon, unit='deg')
        
    def set_longitude(self, longitude):
        """
        Set the location longitude from an astropy Longitude object
        
        >>> cfg = Configuration()
        >>> lon = Longitude(272.3925*u.deg)
        >>> cfg.set_longitude(lon)
        """
        logging.debug('setting longitude to %s' % str(longitude))
        self.config.set('LOCATION', 'longitude', str(longitude.to_value()))
        
    def get_elevation(self):
        """
        Get the location elevation as an astropy Quantity

        >>> cfg = Configuration()
        >>> cfg.get_elevation()
        <Quantity 85. m>
        """
        ele = self.config['LOCATION'].getfloat('elevation')
        return ele*u.m    
        
    def set_elevation(self, elevation):
        """
        Set the location elevation from an astropy Quantity
        
        >>> cfg = Configuration()
        >>> ele = 85*u.m
        >>> cfg.set_elevation(ele)
        """
        logging.debug('setting elevation to %s' % str(elevation))
        self.config.set('LOCATION', 'elevation', str(elevation.to_value()))   

    def get_location(self):
        """
        Get the location as an astropy EarthLocation object

        >>> cfg = Configuration()
        >>> cfg.get_location()
        <EarthLocation (222761.04869822, -5331598.26772541, 3482016.91092873) m>
        """
        return EarthLocation(lat=self.get_latitude(), 
                             lon=self.get_longitude(), 
                             height=self.get_elevation())
        
    def set_location(self, location):
        """
        Set the location latitude, longitude, and elevation from an astropy EarthLocation

        >>> cfg = Configuration()
        >>> loc = EarthLocation(lat=33.30167*u.deg, lon=272.3925*u.deg, height=85*u.m)
        >>> cfg.set_location(loc)
        """
        self.set_latitude(location.lat)
        self.set_longitude(location.lon)
        self.set_elevation(location.height)

    def get_pressure(self):
        """
        Get the location pressure as an astropy Quantity

        >>> cfg = Configuration()
        >>> cfg.get_pressure()
        <Quantity 1013. hPa>
        """
        p = self.config['LOCATION'].getfloat('pressure')
        return p*u.hPa    
        
    def set_pressure(self, pressure):
        """
        Set the location pressure from an astropy Quantity
        
        >>> cfg = Configuration()
        >>> p = 1013*u.hPa
        >>> cfg.set_pressure(p)
        """
        logging.debug('setting pressure to %s' % str(pressure))
        self.config.set('LOCATION', 'pressure', str(pressure.to_value()))   

    def get_temperature(self):
        """
        Get the location temperature as an astropy Quantity

        >>> cfg = Configuration()
        >>> cfg.get_temperature()
        <Quantity 15. deg_C>
        """
        t = self.config['LOCATION'].getfloat('temperature')
        return t*u.Celsius    
        
    def set_temperature(self, temperature):
        """
        Set the location temperature from an astropy Quantity
        
        >>> cfg = Configuration()
        >>> t = 15*u.Celsius
        >>> cfg.set_temperature(t)
        """
        logging.debug('setting temperature to %s' % str(temperature))
        self.config.set('LOCATION', 'temperature', str(temperature.to_value()))   

    def get_rel_humidity(self):
        """
        Get the location relative humidity as a float between 0 and 1

        >>> cfg = Configuration()
        >>> cfg.get_rel_humidity()
        0.75
        """
        return self.config['LOCATION'].getfloat('rel_humidity')
        
    def set_rel_humidity(self, humidity):
        """
        Set the location relative humidity from a float
        
        >>> cfg = Configuration()
        >>> cfg.set_rel_humidity(0.75)
        """
        logging.debug('setting relative humidity to %s' % str(humidity))
        self.config.set('LOCATION', 'rel_humidity', str(humidity))   


    """
    Encoder info
    """
    def get_theta_npr(self):
        """
        Get the npr of the polar encoder
        
        >>> cfg = Configuration()
        >>> cfg.get_theta_npr()
        27196
        """
        return self.config['ENCODERS'].getint('theta_npr')
        
    def set_theta_npr(self, theta_npr):
        """
        Set the npr of the polar encoder
        
        >>> cfg = Configuration()
        >>> cfg.set_theta_npr(2400)
        """
        logging.debug('setting polar npr to %s' % str(theta_npr))
        self.config['ENCODERS']['theta_npr'] = str(theta_npr)

    def get_phi_npr(self):
        """
        Get the npr of the azimuthal encoder
        
        >>> cfg = Configuration()
        >>> cfg.get_phi_npr()
        15507
        """
        return self.config['ENCODERS'].getint('phi_npr')
        
    def set_phi_npr(self, phi_npr):
        """
        Set the npr of the azimuthal encoder
        
        >>> cfg = Configuration()
        >>> cfg.set_phi_npr(2400)
        """
        logging.debug('setting azimuthal npr to %s' % str(phi_npr))
        self.config['ENCODERS']['phi_npr'] = str(phi_npr)

    def get_flip_theta(self):
        """
        Get the polar encoder flip flag
        
        >>> cfg = Configuration()
        >>> cfg.get_flip_theta()
        True
        """
        return self.config['ENCODERS'].getboolean('flip_theta')
        
    def set_flip_theta(self, flip_theta):
        """
        Set the polar encoder flip flag
        
        >>> cfg = Configuration()
        >>> cfg.set_flip_theta(False)
        """
        logging.debug('setting flip_theta to %s' % str(flip_theta))
        self.config['ENCODERS']['flip_theta'] = str(flip_theta)
        
    def get_flip_phi(self):
        """
        Get the azimuthal encoder flip flag
        
        >>> cfg = Configuration()
        >>> cfg.get_flip_phi()
        True
        """
        return self.config['ENCODERS'].getboolean('flip_phi')
        
    def set_flip_phi(self, flip_phi):
        """
        Set the azimuthal encoder flip flag
        
        >>> cfg = Configuration()
        >>> cfg.set_flip_phi(False)
        """
        logging.debug('setting flip_phi to %s' % str(flip_phi))
        self.config['ENCODERS']['flip_phi'] = str(flip_phi)
        
    
    """
    Pointing info
    """
    def get_ia(self):
        """
        Get the index error in azimuth
        
        >>> cfg = Configuration()
        >>> cfg.get_ia()
        0.0
        """
        return self.config['POINTING'].getfloat('ia')
        
    def set_ia(self, value):
        """
        Set the index error in azimuth, units are degrees for now
        
        >>> cfg = Configuration()
        >>> cfg.set_ia(30)
        """
        logging.debug('setting ia to %s' % str(value))
        self.config['POINTING']['ia'] = str(value)

    def get_ie(self):
        """
        Get the index error in elevation
        
        >>> cfg = Configuration()
        >>> cfg.get_ie()
        0.0
        """
        return self.config['POINTING'].getfloat('ie')
        
    def set_ie(self, value):
        """
        Set the index error in elevation, units are degrees for now
        
        >>> cfg = Configuration()
        >>> cfg.set_ie(30)
        """
        logging.debug('setting ie to %s' % str(value))
        self.config['POINTING']['ie'] = str(value)

    def get_an(self):
        """
        Get the north-south misalignment of azimuth axis
        
        >>> cfg = Configuration()
        >>> cfg.get_an()
        0.0
        """
        return self.config['POINTING'].getfloat('an')
        
    def set_an(self, value):
        """
        Set the north-south misalignment of azimuth axis, units are degrees for now
        
        >>> cfg = Configuration()
        >>> cfg.set_an(30)
        """
        logging.debug('setting an to %s' % str(value))
        self.config['POINTING']['an'] = str(value)

    def get_aw(self):
        """
        Get the west-east misalignment of azimuth axis
        
        >>> cfg = Configuration()
        >>> cfg.get_aw()
        0.0
        """
        return self.config['POINTING'].getfloat('aw')
        
    def set_aw(self, value):
        """
        Set the west-east misalignment of azimuth axis, units are degrees for now
        
        >>> cfg = Configuration()
        >>> cfg.set_aw(30)
        """
        logging.debug('setting aw to %s' % str(value))
        self.config['POINTING']['aw'] = str(value)

    def get_ca(self):
        """
        Get the non-perpendicularity of optical axis and elevation axis
        
        >>> cfg = Configuration()
        >>> cfg.get_ca()
        0.0
        """
        return self.config['POINTING'].getfloat('ca')
        
    def set_ca(self, value):
        """
        Set the non-perpendicularity of optical axis and elevation axis, units are degrees for now
        
        >>> cfg = Configuration()
        >>> cfg.set_ca(30)
        """
        logging.debug('setting ca to %s' % str(value))
        self.config['POINTING']['ca'] = str(value)

    def get_npae(self):
        """
        Get the non-perpendicularity of elevation axis and azimuth axis
        
        >>> cfg = Configuration()
        >>> cfg.get_npae()
        0.0
        """
        return self.config['POINTING'].getfloat('npae')
        
    def set_npae(self, value):
        """
        Set the non-perpendicularity of elevation axis and azimuth axis, units are degrees for now
        
        >>> cfg = Configuration()
        >>> cfg.set_npae(30)
        """
        logging.debug('setting npae to %s' % str(value))
        self.config['POINTING']['npae'] = str(value)

    def get_tx(self):
        """
        Get part of (?) the tube flexure
        
        >>> cfg = Configuration()
        >>> cfg.get_tx()
        0.0
        """
        return self.config['POINTING'].getfloat('tx')
        
    def set_tx(self, value):
        """
        Set part of (?) the tube flexure, units are degrees for now
        
        >>> cfg = Configuration()
        >>> cfg.set_tx(30)
        """
        logging.debug('setting tx to %s' % str(value))
        self.config['POINTING']['tx'] = str(value)

    def get_tf(self):
        """
        Get part of (?) the tube flexure
        
        >>> cfg = Configuration()
        >>> cfg.get_tf()
        0.0
        """
        return self.config['POINTING'].getfloat('tf')
        
    def set_tf(self, value):
        """
        Set part of (?) the tube flexure, units are degrees for now
        
        >>> cfg = Configuration()
        >>> cfg.set_tf(30)
        """
        logging.debug('setting tf to %s' % str(value))
        self.config['POINTING']['tf'] = str(value)

    def get_pointing_model(self):
        """
        Get the parameters of the pointing model as a list
        [ia, ie, an, aw, ca, npae, tx, tf]
        
        >>> cfg = Configuration()
        >>> cfg.get_pointing_model()
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        """
        return [self.get_ia(), self.get_ie(), self.get_an(), self.get_aw(),
                self.get_ca(), self.get_npae(), self.get_tx(), self.get_tf()]
        
    def set_pointing_model(self, params):
        """
        Set the parameters of the pointing model from a list
        [ia, ie, an, aw, ca, npae, tx, tf]
        
        >>> cfg = Configuration()
        >>> cfg.set_pointing_model([0, 0, 0, 0, 0, 0, 0, 0])
        """
        if len(params) != 8:
            logging.warn('Pointing model must be a list of 8 floats')
            return
        
        logging.debug('setting pointing model to %s' % str(params))
        self.set_ia(params[0])
        self.set_ie(params[1])
        self.set_an(params[2])
        self.set_aw(params[3])
        self.set_ca(params[4])
        self.set_npae(params[5])
        self.set_tx(params[6])
        self.set_tf(params[7])

    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
    import argparse
    import sys

    "Setup argument parser"
    parser = argparse.ArgumentParser(description='Configuration System')
    parser.add_argument('-p', action='store_true', default=False,
                        help='print the default configuration')
    parser.add_argument('-f', metavar='<filename>', help='filename of configuration to print')
    args = parser.parse_args()

    if args.f:
        config = Configuration(filename=args.f)
        config.config.write(sys.stdout)
    elif args.p:
        config = Configuration()
        config.config.write(sys.stdout)
    
    