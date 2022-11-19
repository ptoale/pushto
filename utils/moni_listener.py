#!/usr/bin/env python
"""
Subscripe to the PushTo monitoring data stream.
"""
import sys
import argparse
import zmq

"Setup argument parser"
parser = argparse.ArgumentParser(description='PushTo Monitoring Utility')
parser.add_argument('host', help='PushTo host')
parser.add_argument('port', help='PushTo monitoring port')
    
args = parser.parse_args()

moni_address = "tcp://%s:%s" % (args.host, args.port)
sys.stdout.write("Subscribing to %s\n" % moni_address)

ctx = zmq.Context()
moni_socket = ctx.socket(zmq.SUB)
moni_socket.subscribe("")
moni_socket.connect(moni_address)

"Sit here and read the output of the server until ^C"
try:
    while True:
        moni = moni_socket.recv_json()
        sys.stdout.write("%s\n" % moni)
except KeyboardInterrupt:
    pass
    
sys.stdout.write("Closing %s\n" % moni_address)
moni_socket.close()
ctx.destroy()
