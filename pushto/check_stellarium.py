#!/usr/bin/env python
"""
Debugging coord transforms...

"""
import logging
import time
import zmq
import numpy as np
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation, SkyCoord, AltAz, Angle
from pushto.config import Configuration
from pushto.stellarium import StellariumTC, StellariumRPC
from pushto.alignment import vec_from_angles
from pushto.messages import Message, CmdMessage

if __name__ == '__main__':

    "Configure the logging"
    logging.basicConfig(
        level=logging.DEBUG,
        #level=logging.INFO,
        format='[%(levelname)-5s] (%(threadName)-10s) %(message)s',
    )
    
    "Use default configuration"
    cfg = Configuration('../pushto_default.cfg')
    
    "Get the location"
    location = cfg.get_location()

    "Setup the address/ports"
    data_sub_address  = "tcp://%s:%s" % (cfg.get_host_ip(), cfg.get_td_eq_port())
    calib_pub_address = "tcp://%s:%s" % (cfg.get_host_ip(), cfg.get_pd_eq_port())

    "Create the rpc"
    rpc = StellariumRPC()

    "Create the zmq context"
    ctx = zmq.Context()

    "Create the STC"
    stc = StellariumTC.setup(cfg, ctx)

    "Create the data publisher (won't be used, but seems necessary)"
    data_pub_socket = ctx.socket(zmq.PUB)
    data_pub_socket.bind(data_sub_address)

    "Create the calib subscriber"
    calib_sub_socket = ctx.socket(zmq.SUB)
    calib_sub_socket.subscribe("")
    calib_sub_socket.connect(calib_pub_address)
    
    "Setup a poller to check for data"
    poller = zmq.Poller()
    poller.register(calib_sub_socket, zmq.POLLIN)
    poller.register(data_pub_socket, zmq.POLLOUT)
    
    "Start the proxy"
    stc.handshake()
    stc.start()
    
    "main loop"
    try:
        while True:
            socks = dict(poller.poll())
            if calib_sub_socket in socks:
                calib = Message.from_json(calib_sub_socket.recv_json())
                stel_altaz = rpc.get_selected_alt_az()
                r1 = vec_from_angles(stel_altaz[0], stel_altaz[1])
                r2 = vec_from_angles(calib.alt, calib.azi)
                phi = 3600*np.degrees(np.arccos(np.dot(r1, r2)))
                print(str(calib))
                print('     RPC: {:10.6f}, {:10.6f}'.format(stel_altaz[0], stel_altaz[1]))
                print(' astropy: {:10.6f}, {:10.6f}'.format(calib.alt, calib.azi))
                print('     phi: ' + str(phi) + ' arcsec')
            
    except KeyboardInterrupt:
        pass

    "Shut it down"
    msg = CmdMessage(cmd='stop')
    data_pub_socket.send_json(msg.to_json())
    time.sleep(1)
        
    "clean up"
    calib_sub_socket.close(linger=1)
    ctx.destroy()
    