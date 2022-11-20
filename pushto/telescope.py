#!/usr/bin/env python
"""
Interface to telescope
    - Handles communication with Arduino connected to serial port, using the :mod:`pyserial` package to create a
      threaded serial reader
    - Transforms data from encoder counts to raw telescope attitude to corrected telescope attitude
    - Publishes data to a :mod:`zmq` PUB socket

Provides:
    - Encoders
    - PointingModel
    - Telescope

"""
import sys
import logging
#
import numpy as np
import serial
import serial.threaded
import zmq
#
from pushto.messages import DataMessage, CmdMessage


class SerialHandler(serial.threaded.LineReader):
    """
    This class is used to handle serial data encoded as utf-8 and terminated with \r\n.
    It uses an Encoders object and a PointingModel object to translate encoder counts
    into telescope attitude and then publishes the results.
    """

    def __init__(self, enc, pm, pub_address, ctx):
        super().__init__()
        self.enc = enc
        self.pm = pm
        self.pub_address = pub_address
        self.ctx = ctx
        self.pubs = None
        
    def __call__(self):
        """
        Must be callable
        """
        return self

    def connection_made(self, transport):
        """
        Pass transport to super
        """
        super().connection_made(transport)
        logging.debug('opened serial port to arduino')

        "Setup PUB socket"
        self.pubs = self.ctx.socket(zmq.PUB)
        self.pubs.bind(self.pub_address)

    def connection_lost(self, exc):
        logging.debug('closed serial port to arduino', exc_info=exc)

    def handle_line(self, line):
        """
        Handle a received line (it's a string!)
        """
        if self.pubs is not None:
            alist = line.split()
            if len(alist) == 5:
                [time, phi_cnt, theta_cnt, phi_err, theta_err] = alist
                logging.debug('got data: %s %s %s %s %s' % (time, phi_cnt, theta_cnt, phi_err, theta_err))
                phi_raw, theta_raw = self.enc.convert(int(phi_cnt), int(theta_cnt))
                phi, theta = self.pm.apply(phi_raw, theta_raw)
                msg = DataMessage(time=time, phi_cnt=phi_cnt, theta_cnt=theta_cnt, 
                                  phi_raw=phi_raw, theta_raw=theta_raw, phi=phi, theta=theta)
                logging.debug('publish data: %s' % msg.to_json())
                self.pubs.send_json(msg.to_json())
            else:
                logging.info('Got write size from Arduino: %s' % alist[0])

    def poison_pill(self):
        """
        Insert the poison pill
        """
        msg = CmdMessage(cmd='stop')
        logging.debug('publish cmd: %s' % msg.to_json())
        self.pubs.send_json(msg.to_json())  # poison pill closes everything else
        self.pubs.close(linger=1)


class Telescope(object):
    """
    Handles the threaded serial reader and publishes the encoder data to a zmq PUB socket.

    :param port: serial port that arduino is connected to
    :type port: str
    :param pub_address: address to publish data to
    :type pub_address: str
    :param ctx: the zmq context to use, optional [None]
    :type ctx: :obj:`zmq.Context`

    >>> scope = Telescope('/dev/cu.usbmodem143301', 'tcp://127.0.0.1:10011')
    >>> scope.start()
    >>> scope.close()
    
    .. note::

       Serial data is expected to be a string terminated with CR LF and containing 5
       interger-parsable fields separated by spaces:
       
          '<msec> <azi_cnt> <alt_cnt> <azi_err> <alt_err>CRLF'

       Published data is a JSON dictionary:
       
          {'time': '2034', 'azi_cnt': '-548', 'alt_cnt': '870', 'azi_err': '0', 'alt_err': '1'}
    
    """

    def __init__(self, port, pub_address, cfg=None, ctx=None):
        self.port = port
        self.pub_address = pub_address
        self.cfg = cfg
        self.ctx = ctx
        self.protocol = None
        self.reader = None

    def start(self):
        """
        Start the reader thread
        """

        "Create and configure the serial object"
        ser = serial.serial_for_url(self.port, do_not_open=True)
        ser.baudrate = 9600

        "Create and configure the protocol object"
        enc = Encoders()
        enc.config(self.cfg)
        pm = PointingModel()
        pm.config(self.cfg)
        self.protocol = SerialHandler(enc, pm, self.pub_address, self.ctx)

        "Open the serial port"
        try:
            ser.open()
            pass
        except serial.SerialException as e:
            logging.error('Could not open serial port {}: {}\n'.format(ser.name, e))
            sys.exit(1)

        "Create the reader thread and start it"
        self.reader = serial.threaded.ReaderThread(ser, self.protocol)
        self.reader.name = 'telescope'
        self.reader.start()

    def close(self):
        """
        Signal to downstream components, close the PUB, and stop the reader thread.
        """
        self.protocol.poison_pill()
        self.reader.close()

    @classmethod
    def setup(cls, cfg, ctx=None):
        """
        Convenience method for creating a Telescope object based on a Configuration object
        
        :param cfg: the configuration object to use
        :type cfg: :obj:`Configuration`
        :param ctx: the zmq context, optional
        :type ctx: :obj:`zmq.Context` or None

        :return: the telescope
        :rtype: :obj:`Telescope`
        """
        ser_port = cfg.get_serial_port()
        pub_address = "tcp://%s:%s" % (cfg.get_host_ip(), cfg.get_td_ta_port())
        
        return Telescope(ser_port, pub_address, cfg=cfg, ctx=ctx)


class Encoders(object):
    """
    Encoders class. Handles transformation from encoder counts to raw attitude.
    
    :param theta_npr: number of counts per revolution, including gearing, of polar encoder
    :type theta_npr: int
    :param phi_npr: number of counts per revolution, including gearing, of azimuthal encoder
    :type phi_npr: int
    :param flip_theta: flip the sense (CW<->CCW) of rotation of the polar encoder
    :type flip_theta: bool
    :param flip_phi: flip the sense (CW<->CCW) of rotation of the azimuthal encoder
    :type flip_phi: bool
    
    >>> encoders = Encoders(phi_npr=2400, theta_npr=2400)
    >>> phi, theta = encoders.convert(1200, 1200)
    """

    def __init__(self, phi_npr=0, theta_npr=0, flip_phi=False, flip_theta=False):
        self.phi_npr = phi_npr
        self.theta_npr = theta_npr
        self.flip_phi = flip_phi
        self.flip_theta = flip_theta
        
    def config(self, cfg):
        """
        Configure encoder parameters from the configuration object.
        
        :param cfg: the configuration
        :type cfg: :obj:`pushto.Configuration`
        
        >>> encoders = Encoders()
        >>> encoders.config(cfg)
        >>> phi, theta = encoders.convert(1200, 1200)
        """
        self.phi_npr = cfg.get_phi_npr()
        self.theta_npr = cfg.get_theta_npr()
        self.flip_phi = cfg.get_flip_phi()
        self.flip_theta = cfg.get_flip_theta()
        
    def convert(self, phi_cnt, theta_cnt):
        """
        Convert from encoder counts to raw telescope attitude (phi, theta)
    
        :param phi_cnt: count of azimuthal encoder
        :type phi_cnt: long
        :param theta_cnt: count of polar encoder
        :type theta_cnt: long
        
        :return: theta and phi, in degrees
        :rtype: list(float)
        """

        "Reverse the sense of the counters if necessary"
        if self.flip_phi:
            phi_cnt *= -1
        if self.flip_theta:
            theta_cnt *= -1

        "For phi: convert counts into an angle in range [0:360]"
        phi = phi_cnt*360./self.phi_npr
        if phi >= 360:
            phi -= 360*np.fix(phi/360)
        elif phi < 0:
            phi += 360*(1-np.fix(phi/360))
        
        "For theta: convert counts into an angle in range [-180:+180]"
        theta = theta_cnt*360./self.theta_npr
        if theta >= 360:
            theta -= 360*np.fix(theta/360)
        elif theta < 0:
            theta += 360*(1-np.fix(theta/360))
        if theta > 180:
            theta -= 360
    
        "Now convert to spherical angles"
        if theta > 90:
            theta = 180 - theta
            phi = (phi + 180) % 360
        elif theta < -90:
            theta = -180 - theta
            phi = (phi + 180) % 360

        return phi, theta


class PointingModel(object):
    """
    8 parameter pointing model of Tpoint

    Handles transformation from raw attitude to corrected attitude    
    
    :param ia: index error in azimuth
    :type ia: float
    :param ie: index error in elevation
    :type ie: float
    :param an: north-south misalignment of azimuth axis
    :type an: float
    :param aw: west-east misalignment of azimuth axis
    :type aw: float
    :param ca: non-perpendicularity of optical axis and elevation axis
    :type ca: float
    :param npae: non-perpendicularity of elevation axis and azimuth axis
    :type npae: float
    :param tx: tube flexure term proportional to cot(el)
    :type tx: float
    :param tf: tube flexure term proportional to cos(el)
    :type tf: float

    >>> pm = PointingModel()
    >>> phi, theta = pm.apply(180, 45)
    """

    def __init__(self, ia=0, ie=0, an=0, aw=0, ca=0, npae=0, tx=0, tf=0):
        self.ia = ia
        self.ie = ie
        self.an = an
        self.aw = aw
        self.ca = ca
        self.npae = npae
        self.tx = tx
        self.tf = tf

    def config(self, cfg):
        """
        Configure pointing model from the configuration object.
        
        :param cfg: the configuration
        :type cfg: :obj:`pushto.Configuration`
        
        >>> pm = PointingModel()
        >>> pm.config(cfg)
        >>> phi, theta = pm.apply(180, 45)
        """
        self.ia = cfg.get_ia()
        self.ie = cfg.get_ie()
        self.an = cfg.get_an()
        self.aw = cfg.get_aw()
        self.ca = cfg.get_ca()
        self.npae = cfg.get_npae()
        self.tx = cfg.get_tx()
        self.tf = cfg.get_tf()
        
    def apply(self, phi, theta):
        """
        Convert from raw telescope attitude to corrected telescope attitude
    
        :param phi: raw azimuthal angle
        :type phi: float
        :param theta: raw altitude angle
        :type theta: float
        
        :return: phi and theta, in degrees
        :rtype: list(float)
        """

        phi_r = np.radians(phi)
        theta_r = np.radians(theta)

        "azimuth corrections"
        da = -1 * self.ia
        da -= self.an * np.sin(phi_r) * np.tan(theta_r)
        da -= self.aw * np.cos(phi_r) * np.tan(theta_r)
        if abs(theta) != 90:
            da -= self.ca / np.cos(theta_r)
        da -= self.npae * np.tan(theta_r)

        azi = phi + da/3600
        if azi >= 360:
            azi -= 360*np.fix(azi/360)
        elif phi < 0:
            azi += 360*(1-np.fix(azi/360))

        "elevation corrections"
        de = self.ie
        de -= self.an * np.cos(phi_r)
        de += self.aw * np.sin(phi_r)
        de -= self.tf * np.cos(theta_r)
        if theta != 0:
            de -= self.tx / np.tan(theta_r)
    
        alt = theta + de/3600
        if alt >= 360:
            alt -= 360*np.fix(alt/360)
        elif alt < 0:
            alt += 360*(1-np.fix(alt/360))
        if alt > 180:
            alt -= 360

        "Now convert to spherical angles"
        if alt > 90:
            alt = 180 - alt
            azi = (azi + 180) % 360
        elif alt < -90:
            alt = -180 - alt
            azi = (azi + 180) % 360

        return azi, alt
        
    def deapply(self, azi, alt):
        """
        need to find the phi, theta that make apply(phi,theta) - (azi,alt) = 0
        
        """
        return None


if __name__ == '__main__':
    import argparse
    from pushto.config import Configuration
    
    """
    This demonstrates how to use it.
        - must have a serial port to connect to: actual or fake
            actual:
            fake:
        - we create a SUB and subscribe to the Telescope PUB
        - print the received data
    """
    
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

    "Configure zmq"
    pub_address = 'tcp://%s:%s' % (cfg.get_host_ip(), cfg.get_td_ta_port())
    ctx = zmq.Context()
    subs = ctx.socket(zmq.SUB)
    subs.subscribe("")
    subs.connect(pub_address)

    "Configure serial port"
    if args.port:
        cfg.set_serial_port(args.port)

    "Create the server and start it"
    telescope = Telescope.setup(cfg, ctx)
    telescope.start()
    
    "Sit here and read the output of the server until ^C"
    try:
        while True:
            data = subs.recv_json()
            logging.info("On SUB: %s" % data)
    except KeyboardInterrupt:
        logging.info('keyboard interrupt')
        
    "Clean up"
    telescope.close()
    subs.close()
    ctx.destroy()
