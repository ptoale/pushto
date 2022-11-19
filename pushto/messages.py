#!/usr/bin/env python
"""
Messages

    - data: azi_cnt, alt_cnt, phi, theta, azi, alt, ra, dec
"""

message_types = ('DATA', 'ALIGN', 'CMD')

class Message(object):
    """
    Base class for messages.
    """

    def __init__(self, *args, **kwargs):
        self.type = kwargs['type']
        self.msg = {'type': self.type,}

    def __repr__(self):
        return str(self.msg)

    @classmethod
    def from_json(cls, data):
        if data['type'] == 'DATA':
            return DataMessage(**data)
        elif data['type'] == 'ALIGN':
            return AlignMessage(**data)
        elif data['type'] == 'CMD':
            return CmdMessage(**data)
        else:
            return None

class CmdMessage(Message):

    def __init__(self, *args, **kwargs):
        super().__init__(type='CMD')

        self.cmd = kwargs['cmd'] if 'cmd' in kwargs else None
        self.opt = kwargs['opt'] if 'opt' in kwargs else None

        self.msg = self.to_json()
            
    def to_json(self):
        self.msg['cmd'] = self.cmd
        self.msg['opt'] = self.opt
        return self.msg

class DataMessage(Message):
    """
    Unified key names for the various coordinate systems.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(type='DATA')
        
        self.time      = kwargs['time']      if 'time'      in kwargs else None
        self.phi_cnt   = kwargs['phi_cnt']   if 'phi_cnt'   in kwargs else None
        self.theta_cnt = kwargs['theta_cnt'] if 'theta_cnt' in kwargs else None
        self.phi_raw   = kwargs['phi_raw']   if 'phi_raw'   in kwargs else None
        self.theta_raw = kwargs['theta_raw'] if 'theta_raw' in kwargs else None
        self.phi       = kwargs['phi']       if 'phi'       in kwargs else None
        self.theta     = kwargs['theta']     if 'theta'     in kwargs else None
        self.azi       = kwargs['azi']       if 'azi'       in kwargs else None
        self.alt       = kwargs['alt']       if 'alt'       in kwargs else None
        self.ra        = kwargs['ra']        if 'ra'        in kwargs else None
        self.dec       = kwargs['dec']       if 'dec'       in kwargs else None

        self.msg = self.to_json()
        
    def to_json(self):
        self.msg['time']      = self.time
        self.msg['phi_cnt']   = self.phi_cnt
        self.msg['theta_cnt'] = self.theta_cnt
        self.msg['phi_raw']   = self.phi_raw
        self.msg['theta_raw'] = self.theta_raw
        self.msg['phi']       = self.phi
        self.msg['theta']     = self.theta
        self.msg['azi']       = self.azi
        self.msg['alt']       = self.alt
        self.msg['ra']        = self.ra
        self.msg['dec']       = self.dec
        return self.msg

class AlignMessage(Message):
    """
    Unified key names for the various coordinate systems.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(type='ALIGN')
        
        self.time = kwargs['time'] if 'time' in kwargs else None
        self.azi  = kwargs['azi']  if 'azi'  in kwargs else None
        self.alt  = kwargs['alt']  if 'alt'  in kwargs else None
        self.ra   = kwargs['ra']   if 'ra'   in kwargs else None
        self.dec  = kwargs['dec']  if 'dec'  in kwargs else None

        self.msg = self.to_json()
        
    def to_json(self):
        self.msg['time'] = self.time
        self.msg['azi']  = self.azi
        self.msg['alt']  = self.alt
        self.msg['ra']   = self.ra
        self.msg['dec']  = self.dec
        return self.msg


if __name__ == '__main__':

    "ArduinoProxy creates a DataMessage with time, phi_cnt, and theta_cnt"
    ap_msg = DataMessage(time = 123, phi_cnt = 1000, theta_cnt = -100)
    
    "It then writes it to the PUB socket"
    ap_msg_json = ap_msg.to_json()
    print("AP PUB: %s" % ap_msg_json)

    "It is recieved by PushTo"
    pt_msg = Message.from_json(ap_msg_json)
    print("PT SUB: %s" % pt_msg.to_json())  
    
    "It then updates the other fields"
    pt_msg.time = 234
    pt_msg.phi = 15
    pt_msg.theta = 30
    pt_msg.azi = 20
    pt_msg.alt = 35
    pt_msg.ra = 25
    pt_msg.dec = 40
    
    "And writes it to its PUB socket"
    pt_msg_json = pt_msg.to_json()
    print("PT PUB: %s" % pt_msg_json)

    "It is recieved by StellariumProxy"
    sp_msg = Message.from_json(pt_msg_json)
    print("SP SUB: %s" % sp_msg.to_json())  

    
    "Create a CmdMessage"
    cmd = CmdMessage(cmd='Stop')
    cmd_json = cmd.to_json()
    print(cmd_json)
    
    "Create a AligndMessage"
    am = AlignMessage(time = 321, ra=55, dec=-10, azi=350, alt=34)
    am_json = am.to_json()
    print(am_json)
    
    

    