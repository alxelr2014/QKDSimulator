import numpy as np
from ..qstate import Coherent
from ..qdevices import BeamSplitter,PhotonDetector
from .qkd_protocol import QKDProtocol


class DPS(QKDProtocol):
    def __init__(self,):
        self.prev_del_line = Coherent(0)

    def signal_generation(self,params):
        alpha = params['alpha']
        bits = np.random.rand() <= 1/2
        signal =Coherent((-1)**(bits)*alpha)
        return {'signal':signal, 'abits':bits,'time': params['time']}

    def detection(self,params):
        if params['dark_count'][0]:
            return {'m0_detector':1,'m1_detector':0,'time':params['time']}
        if params['dark_count'][1]:
            return {'m0_detector':0,'m1_detector':1,'time':params['time']} 
    
        received= params['received']
        cd_lines = BeamSplitter(0.5).transmit(received)
        curr_line = cd_lines[0]
        del_lin = cd_lines[1]
        measure_lines = BeamSplitter(0.5).transmit(np.array([curr_line,self.prev_del_line]))
        m0_detector = PhotonDetector().measure(measure_lines[0])
        m1_detector = PhotonDetector().measure(measure_lines[1])
        self.prev_del_line = del_lin
        return {'m0_detector' : m0_detector, 'm1_detector': m1_detector, 'time':params['time']}

    def sift(self,aparams,bparams):
        abits = aparams['abits']
        m0_detector = bparams['m0_detector']
        m1_detector = bparams['m1_detector']
        bob_message = np.logical_or(m0_detector, m1_detector)
        # note the the first clicks are dont cares
        # TODO: is that true?
        num_clicks = bob_message.sum()-bob_message[0]
        if num_clicks <= 0:
            raise RuntimeError("DPS protocol produced no keys. Aborted!")
        
            
        alice_key = np.full(num_clicks,-1)
        bob_key = np.full(num_clicks,-1)
        key_ind = 0
        for _ in range(1,len(bob_message)):
            if bob_message[_]:
                alice_key[key_ind] = 1- (abits[_] ^ abits[_-1])
                bob_key[key_ind] = 1 - m0_detector[_]
                key_ind += 1

        return {'akey': alice_key.astype(int), 'bkey': bob_key.astype(int)}
    
    
    def param_est(self,params):
        return super().param_est(params)
 