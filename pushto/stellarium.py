#!/usr/bin/env python
"""
Interface to Stellarium Telescope Control plugin.

Provides:
    - stc_encode
    - stc_decode
    - StellariumTC
    - StellariumRPC

"""
import logging
import socket
import threading
#
import requests
import zmq
from astropy.time import Time
#
from pushto.messages import Message, AlignMessage


def stc_encode(utc, ra, dec):
    """
    Encode a messsage for the Stellarium Telescope Control. 
    This is always a 'CurrentPosition' message.
        
    :param utc: time 
    :type utc: iso-formated string
    :param ra: right ascension, in hours
    :type ra: float
    :param dec: declination, in degrees
    :type dec: float
        
    :return: encoded data
    :rtype: bytearray
        
    The message is 24B composed of:
        - size    (2B): should be 24
        - type    (2B): should be 0
        - time    (8B): microseconds since epoch
        - ra_int  (4B): value in range 0 to 4294967295
        - dec_int (4B): value in range -1073741824 to +1073741824
        - status  (4B): status, 0 means ok

    >>> data = stc_encode(utc='2022-11-17T16:14:58.967345+00:00', ra=16.0, dec=70.0)
    
    """
        
    "convert ISO utc time into timestamp (microseconds since epoch)"
    utc = Time(utc, format='iso')
    timestamp = int(1e6*utc.unix)
        
    "convert ra and dec into integer representation"
    ra_int = int(ra*2147483648/12.0)
    dec_int = int(dec*1073741824/90.0)

    size = 24
    mtype = 0
    status = 0

    "create and pack the bytearray"
    data = bytearray(24)
    data[ 0: 2] = int(size).to_bytes(2, 'little')
    data[ 2: 4] = int(mtype).to_bytes(2, 'little')
    data[ 4:12] = int(timestamp).to_bytes(8, 'little')
    data[12:16] = ra_int.to_bytes(4, 'little')
    data[16:20] = dec_int.to_bytes(4, 'little', signed=True)
    data[20:24] = int(status).to_bytes(4, 'little')     

    logging.debug('stc_encode: %s %s %s %s %s %s' % (size, mtype, timestamp, ra_int, dec_int, status))
    logging.debug('stc_encode: %s' % str(data))

    return data


def stc_decode(data):
    """
    Decode a message from the Stellarium Telescope Control. 
    This will always be a 'Slew' command.
        
    :param data: data read from Stellarium socket
    :type data: bytes
        
    :return: (utc, ra, dec)
    :rtype: list(str, float, float)
        
    The message is 20B composed of:
        - size    (2B): should be 20
        - type    (2B): should be 0
        - time    (8B): microseconds since epoch
        - ra_int  (4B): value in range 0 to 4294967295
        - dec_int (4B): value in range -1073741824 to +1073741824
        
    """
    
    "Unpack the bytearray"
    size    = int.from_bytes(data[ 0: 2], 'little')
    mtype   = int.from_bytes(data[ 2: 4], 'little')
    time    = int.from_bytes(data[ 4:12], 'little')
    ra_int  = int.from_bytes(data[12:16], 'little')
    dec_int = int.from_bytes(data[16:20], 'little', signed=True)

    logging.debug('stc_decode: %s' % str(data))
    logging.debug('stc_decode: %s %s %s %s %s' % (size, mtype, time, ra_int, dec_int))
        
    "The time is microseconds since epoch, convert it to utc"
    utc = Time(time/1e6, format='unix').iso
        
    "Now convert the ra_int and dec_int into angles"
    ra = ra_int*12.0/2147483648    # in hours
    dec = dec_int*90.0/1073741824  # in deg
    if dec > 180:
        dec -= 360

    return utc, ra, dec


class StellariumRPC(object):
    """
    Handles interactions with the Stellarium Remote Control plugin.
    
    :param api_url: url of rpc api, defaults to 'http://localhost:8090/api'
    :type api_url: str or None
    
    >>> rpc = StellariumRPC()
    
    """
    
    DEFAULT_API_URL = 'http://localhost:8090/api'
    
    def __init__(self, api_url=DEFAULT_API_URL):
        self.api_url = api_url
        
        self.action_id = -2
        self.prop_id = -2
        
    def get_status(self):
        """
        Get Stellarium status
        
        :return: status
        :rtype: dict
        
        """
        url = self.api_url + "/main/status?propId=" + str(self.prop_id) + "&actionId=" + str(self.action_id)
        contents = requests.get(url).json()
        self.prop_id = contents['propertyChanges']['id']
        self.action_id = contents['actionChanges']['id']
        return contents

    def get_selected_info(self):
        """
        Get info on selected target in Stellarium
            
        :return: alot of info
        :rtype: dict
        
        """
        url = self.api_url + "/objects/info"
        return requests.get(url, params={'format': 'json'}).json()

    def get_utc(self):
        """
        Get Stellarium utc time
            need to remove the trailing 'Z' from the 'utc' field

        :return: Stellarium UTC
        :rtype: :obj:`astropy.time.Time`

        """
        status = self.get_status()
        return Time(status['time']['utc'][:-1], format='iso') 

    def get_selected_alt_az(self):
        """
        Get a selected target's Alt and Az at the current time (p+n corrected) 
        and location in Stellarium
            
        :return: Alt, Az in decimal degrees
        :rtype: list(float)
        
        .. note::
        
            The object Alt-Az do not update if the Stellarium app is not in focus!!!
        
        """
        info = self.get_selected_info()
        return info['altitude'], info['azimuth']

    def get_selected_ra_dec(self):
        """
        Get a selected target's RA and Dec
            
        :return: RA, Dec in decimal degrees
        :rtype: list(float)
        
        """
        info = self.get_selected_info()
        return info['ra'], info['dec']

    def select_target(self, target):
        """
        Select a target in Stellarium
    
        :param target: name of target to select
        :type target: str
        
        :return: status
        :rtype: bool

        """
        url = self.api_url + "/main/focus"
        return requests.post(url, data={'target': target})

    def set_time_to_now(self):
        """
        Set the time to current time
            
        :return: status
        :rtype: bool

        """
        url = self.api_url + "/stelaction/do"
        return requests.post(url, data={'id': 'actionReturn_To_Current_Time'}).text

    def list_actions(self):
        url = self.api_url + "/stelaction/list"
        return requests.get(url).json()


class StellariumTC(threading.Thread):
    """
    Handles communications with the Stellarium Telescope Control (STC) over a tcp socket.
    
    :param stel_host: host on which Stellarium is running
    :type stel_host: str
    :param stel_port: port on which STC will connect
    :type stel_port: int
    :param data_sub_address: address to subscribe to the data stream
    :type data_sub_address: str in form 'tcp://127.0.0.1:10001'
    :param calib_pub_address: address to publish calibration data
    :type calib_pub_address: str in form 'tcp://127.0.0.1:10001'
    :param ctx: the :mod:`zmq` context, optional
    :type ctx: :obj:`zmq.Context` or None

    >>> stel = StellariumTC('localhost', 10002, 'tcp://127.0.0.1:10012', 'tcp://127.0.0.1:10013')
    >>> stel.handshake()
    >>> stel.start()
    >>> stel.close()
    
    .. note::

       RAW: connection to Stellarium
    
       - can send MoveTo commands with RA/Dec
       - can receive SlewTo commands with RA/Dec (requires pushing the button within Stellarium)
    
       SUB: connection to control
    
       - receives telescope direction in RA/Dec

       PUB: connection to control
       
       - sends SlewTo RA/Dec to control

    """

    def __init__(self, stel_host, stel_port, data_sub_address, calib_pub_address, ctx=None):
        super().__init__(daemon=True, name='stellarium')
        
        "configure the raw socket"
        self.serverAddress = (stel_host, stel_port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.serverAddress)
        self.sock.settimeout(600)  # Throws a timeout exception if connections are idle for 10 minutes
        self.sock.listen(1)        # set the socket to listen, now it's a server!
        self.connection = None

        "configure the zmq sockets"
        self.data_sub_address = data_sub_address
        self.calib_pub_address = calib_pub_address
        self.ctx = ctx
        if self.ctx is None:
            self.ctx = zmq.Context()
            
        self.data_sub_socket = self.ctx.socket(zmq.SUB)
        self.data_sub_socket.subscribe("")
        
        self.calib_pub_socket = self.ctx.socket(zmq.PUB)
        self.calib_pub_socket.bind(self.calib_pub_address)

    def handshake(self):
        """
        Establish a connection with the STC.
        """
        try:
            while True:
                logging.debug('attempting handshake')
                self.connection, clientAddress = self.sock.accept()
                if self.connection is not None:
                    logging.debug('connected to Stellarium')
                    break
        except Exception as e:
            logging.error("failed handshake with Stellarium: %s" % e)

    def close(self):
        """
        Close connections and sockets.
        """
        self.data_sub_socket.close(linger=1)
        self.calib_pub_socket.close(linger=1)
        self.connection.close()
        self.sock.close()
        logging.debug('disconnected from Stellarium')
        
    def run(self):
        """
        Need to listen on socket for requests
        For each request, need to forward to stellarium over raw socket
        """
        
        "connect the SUB socket"
        self.data_sub_socket.connect(self.data_sub_address)
        
        "setup the poller to listen to the SUB and RAW sockets for input"
        poller = zmq.Poller()
        poller.register(self.data_sub_socket, zmq.POLLIN)
        poller.register(self.connection.fileno(), zmq.POLLIN)

        while True:
            "Poll the poller for incoming messages"
            socks = dict(poller.poll())
            if self.data_sub_socket in socks:
                data_msg = self.data_sub_socket.recv_json()
                msg = Message.from_json(data_msg)
                logging.debug('SUB: %s' % msg)
                if msg.type == 'DATA':
                    data = stc_encode(msg.time, msg.ra, msg.dec)
                    self.connection.send(data)
                elif msg.type == 'CMD':
                    if msg.cmd == 'stop':
                        "shut it down"
                        self.close()
                        return

            if self.connection.fileno() in socks:
                "decode the data, this will only be a 'slew to'"
                data = self.connection.recv(640)
                utc, ra, dec = stc_decode(data)

                "publish alignment data"
                msg = AlignMessage(time=utc, ra=ra, dec=dec)
                logging.debug('PUB: %s' % msg.to_json())
                self.calib_pub_socket.send_json(msg.to_json())

    @classmethod
    def setup(cls, cfg, ctx=None):
        """
        Convenience method for creating a StellariumTC object based on a Configuration object
        
        :param cfg: the configuration object to use
        :type cfg: :obj:`Configuration`
        :param ctx: the zmq context, optional
        :type ctx: :obj:`zmq.Context` or None

        :return: the stellarium TC
        :rtype: :obj:`StellariumTC`
        """        
        control_pub_address = "tcp://%s:%s" % (cfg.get_host_ip(), cfg.get_td_eq_port())
        stellar_pub_address = "tcp://%s:%s" % (cfg.get_host_ip(), cfg.get_pd_eq_port())

        return StellariumTC(stel_host=cfg.get_host_ip(),
                            stel_port=cfg.get_stc_port(),
                            data_sub_address=control_pub_address,
                            calib_pub_address=stellar_pub_address,
                            ctx=ctx)

   
if __name__ == '__main__':
    import time
    from pushto.config import Configuration
    from pushto.messages import DataMessage, CmdMessage

    "Configure the logging"
    logging.basicConfig(
        #level=logging.DEBUG,
        level=logging.INFO,
        format='[%(levelname)-5s] (%(threadName)-10s) %(message)s',
    )

    cfg = Configuration()
    ctx = zmq.Context()
    stc = StellariumTC.setup(cfg, ctx)

    data_sub_address = "tcp://%s:%s" % (cfg.get_host_ip(), cfg.get_td_eq_port())
    calib_pub_address = "tcp://%s:%s" % (cfg.get_host_ip(), cfg.get_pd_eq_port())
    
    data_pub_socket = ctx.socket(zmq.PUB)
    data_pub_socket.bind(data_sub_address)
    calib_sub_socket = ctx.socket(zmq.SUB)
    calib_sub_socket.subscribe("")
    calib_sub_socket.connect(calib_pub_address)
    poller = zmq.Poller()
    poller.register(calib_sub_socket, zmq.POLLIN)
    poller.register(data_pub_socket, zmq.POLLOUT)
    
    stc.handshake()
    stc.start()
    
    try:
        RA = 0.
        Dec = 70.
        while True:
        
            socks = dict(poller.poll())
            if data_pub_socket in socks:
                utc = Time.now().iso
                msg = DataMessage(time=utc, ra=RA, dec=Dec)
                logging.info("Sending: %s" % msg.to_json())
                data_pub_socket.send_json(msg.to_json())
                time.sleep(0.5)
                RA += 1
                RA = RA % 24
            
            if calib_sub_socket in socks:
                data = calib_sub_socket.recv_json()
                msg = Message.from_json(data)
                logging.info("Receiving: %s" % msg)

    except KeyboardInterrupt:
        logging.info('keyboard interrupt')
    
    "Shut it down"
    msg = CmdMessage(cmd='stop')
    logging.info("Sending: %s" % msg.to_json())
    data_pub_socket.send_json(msg.to_json())
    time.sleep(1)
    
    data_pub_socket.close(linger=1)
    calib_sub_socket.close(linger=1)
    ctx.destroy()
    
