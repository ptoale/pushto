#!/usr/bin/env python
"""
Handles site-dependent transformations between the telescope attitude and equatorial
coordinates.

Provides:
    - Location
    - Site

"""
import logging
import threading
#
import zmq
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, SkyCoord
#
from pushto.stellarium import StellariumTC
from pushto.telescope import Telescope
from pushto.alignment import Aligner
from pushto.messages import Message

class Location(object):
    """
    Location object.
    
    :param lat: site latitude in degrees
    :type lat: float
    :param lon: site longitude in degrees
    :type lon: float
    :param elev: site elevation in meters
    :type elev: float
    :param pres: site pressure in hPa
    :type pres: float
    :param temp: site temperature in Celsius
    :type temp: float
    :param relh: site relative humidity
    :type relh: float

    """

    def __init__(self, lat, lon, elev, pres=0, temp=0, relh=0):
        self.location = EarthLocation(lat=lat, lon=lon, height=elev)
        self.pres = pres
        self.temp = temp
        self.relh = relh
    
    def horizontal_to_equatorial(self, azi, alt, utc=None):
        """
        Convert from horizontal to equatorial coordinates.
        
        :param azi: local azimuth in degrees
        :type azi: float
        :param alt: local altitude in degrees
        :type alt: float
        :param utc: utc time, optional (default is current utc)
        :type utc: :obj:`astropy.time.Time` or None
        
        :return: ra in hours, dec in degrees
        :rtype: list(floats)
        
        """
        if utc is None: utc = Time.now()
        altaz = AltAz(obstime=utc, location=self.location, 
                      pressure=self.pres, temperature=self.temp,
                      relative_humidity=self.relh, obswl=550*u.nm)
        icrs = SkyCoord(alt=alt*u.deg, az=azi*u.deg, frame=altaz).transform_to('icrs')
    
        return icrs.ra.to_value()*24/360, icrs.dec.to_value()
        
    def equatorial_to_horizontal(self, ra, dec, utc=None):
        """
        Convert from equatorial to horizontal coordinates.
        
        :param ra: right ascension in hours
        :type ra: float
        :param dec: declination in degrees
        :type dec: float
        :param utc: utc time, optional (default is current utc)
        :type utc: :obj:`astropy.time.Time` or None
        
        :return: azi in degrees, alt in degrees
        :rtype: list(floats)
        
        """
        if utc is None: utc = Time.now()
        altaz = AltAz(obstime=utc, location=self.location, 
                      pressure=self.pres, temperature=self.temp,
                      relative_humidity=self.relh, obswl=550*u.nm)
        hori = SkyCoord(ra=(ra*360/24)*u.deg, dec=dec*u.deg, frame='icrs').transform_to(altaz)
    
        return hori.az.to_value(), hori.alt.to_value()
    
    @classmethod
    def setup(cls, cfg):
        lat  = cfg.get_latitude()
        lon  = cfg.get_longitude()
        elev = cfg.get_elevation()
        pres = cfg.get_pressure()
        temp = cfg.get_temperature()
        relh = cfg.get_rel_humidity()
        return Location(lat, lon, elev, pres, temp, relh)
        
class Site(threading.Thread):
    """
    PushTo class
    
    :param td_ta_address: telescope data/telescope attitude address
    :type td_ta_address: str
    :param td_eq_address: telescope data/equatorial address
    :type td_eq_address: str
    :param pd_eq_address: pointing data/equatorial address
    :type pd_eq_address: str
    :param pd_ta_address: pointing data/telescope attitude address
    :type pd_ta_address: str
    :param location: the location of the telescope
    :type location: :obj:`pushto.site.Location`
    :param ctx: :mod:`zmq` context, optional
    :type ctx: :obj:`zmq.Context` or None
    
    >>> site = Site.setup(cfg, ctx)
    >>> site.connect()
    >>> site.start()
    >>> site.close()

    """
    
    def __init__(self, td_ta_address, td_eq_address, pd_eq_address, pd_ta_address, 
                 location, ctx=None):
        super().__init__(daemon=True, name='site')
   
        "process arguments"
        self.td_ta_address = td_ta_address
        self.td_eq_address = td_eq_address
        self.pd_eq_address = pd_eq_address
        self.pd_ta_address = pd_ta_address
        self.location = location
        if ctx is None:
            ctx = zmq.Context()

        "setup communications"
        self.td_ta_socket = ctx.socket(zmq.SUB)
        self.td_ta_socket.subscribe("")
        self.td_eq_socket = ctx.socket(zmq.PUB)
        self.pd_eq_socket = ctx.socket(zmq.SUB)
        self.pd_eq_socket.subscribe("")
        self.pd_ta_socket = ctx.socket(zmq.PUB)
        
        self.aligner = Aligner()
     
    def close(self):
        """
        Close all sockets.
        """
        logging.debug('closing the sockets')
        self.td_ta_socket.disconnect(self.td_ta_address)
        self.pd_eq_socket.disconnect(self.pd_eq_address)
        self.td_ta_socket.close(linger=1)
        self.pd_eq_socket.close(linger=1)
        self.td_eq_socket.close(linger=1)
        self.pd_ta_socket.close(linger=1)


    def connect(self):
        """
        Bind and connect the sockets.
        """
        logging.debug('connecting the sockets')
        self.td_ta_socket.connect(self.td_ta_address)
        self.td_eq_socket.bind(self.td_eq_address)
        self.pd_eq_socket.connect(self.pd_eq_address)
        self.pd_ta_socket.bind(self.pd_ta_address)

    def run(self):
        logging.debug('entering run...')
        
        """
        need to listen to 2 sockets:
        """
        poller = zmq.Poller()
        poller.register(self.td_ta_socket, zmq.POLLIN)
        poller.register(self.pd_eq_socket, zmq.POLLIN)
        
        last_data = None
        N = 10  # with T_arduino=50ms --> 500ms   Stellarium is smooth with N=10!
        n = 0
        time = Time.now()
        while True:
            "Poll the poller for incoming messages"
            socks = dict(poller.poll())
        
            if self.td_ta_socket in socks:
                data_msg = self.td_ta_socket.recv_json()
                msg = Message.from_json(data_msg)
                logging.debug('TD SUB: %s' % msg)
                
                if msg.type == 'CMD':
                    if msg.cmd == 'stop':
                        logging.info("Sending kill signal to Stellarium: %s" % data_msg)
                        self.td_eq_socket.send_json(data_msg)
                        self.close()
                        return
                elif msg.type == 'DATA':
                    n += 1
                
                    """
                    Transform from TA to EQ
                        - theta,phi -> alt,azi: requires alignment calibration
                        - alt,azi -> dec, ra:   requires time and location
                    """
                    phi = msg.phi
                    theta = msg.theta
                    alt, azi = self.aligner.telescope_to_horizontal(theta, phi)
                    ra, dec = self.location.horizontal_to_equatorial(azi, alt)
                    msg.time = Time.now().iso
                    msg.alt = alt
                    msg.azi = azi
                    msg.ra = ra
                    msg.dec = dec

                    "Store for alignment"
                    last_data = msg.to_json()
                    
                    if (n%N) == 0:
                        "Send RA, Dec to stellarium"
                        self.td_eq_socket.send_json(msg.to_json())
                        logging.info("On data PUB: %s" % msg.to_json())

            if self.pd_eq_socket in socks:
                calib_msg = self.pd_eq_socket.recv_json()
                logging.info("On calib SUB: %s" % calib_msg)
                msg = Message.from_json(calib_msg)

                azi, alt = self.location.equatorial_to_horizontal(msg.ra, msg.dec, Time(msg.time, format='iso'))                
                self.aligner.add_star(last_data['theta'], last_data['phi'], alt, azi)                    

                theta, phi = self.aligner.horizontal_to_telescope(alt, azi)
                msg.azi = azi
                msg.alt = alt
                msg.theta = theta
                msg.phi = phi
                self.pd_ta_socket.send_json(msg.to_json())

    def reset_alignment(self):
        """
        Reset the alignment data.
        """
        self.aligner.reset()
        
    @classmethod
    def setup(cls, cfg, ctx=None):

        td_ta_address = "tcp://%s:%s" % (cfg.get_host_ip(), cfg.get_td_ta_port())
        td_eq_address = "tcp://%s:%s" % (cfg.get_host_ip(), cfg.get_td_eq_port())
        pd_eq_address = "tcp://%s:%s" % (cfg.get_host_ip(), cfg.get_pd_eq_port())
        pd_ta_address = "tcp://%s:%s" % (cfg.get_host_ip(), cfg.get_pd_ta_port())
        location = Location.setup(cfg)
   
        return Site(td_ta_address, td_eq_address, pd_eq_address, pd_ta_address, 
                    location, ctx)

if __name__ == '__main__':
    import argparse
    import time
    from config import Configuration

    "Setup argument parser"
    parser = argparse.ArgumentParser(description='Telescope Server')
    parser.add_argument('--port', help='serial port connected to arduino')
    parser.add_argument('-d', action='store_true', default=False,
                        help='enable debug logging')  
    args = parser.parse_args()

    "Configure the logging"
    level = logging.INFO
    if args.d:
        level = logging.DEBUG
    logging.basicConfig(
        level=level,
        format='[%(levelname)-5s] (%(threadName)-10s) %(message)s',
    )
    
    cfg = Configuration()
    ctx = zmq.Context()

    "Configure serial port"
    if args.port:
        cfg.set_serial_port(args.port)

    """
    Start stellarium first
    """
    stellarium = StellariumTC.setup(cfg, ctx)
    stellarium.handshake()
    stellarium.start()

    """
    Start arduino second
    """
    telescope = Telescope.setup(cfg, ctx)
    telescope.start()
    
    """
    Start pushto third
    """
    site = Site.setup(cfg, ctx)
    site.connect()
    site.start()
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logging.info('keyboard interupt')
        
    telescope.close()
    time.sleep(1)    
    ctx.destroy()
    
