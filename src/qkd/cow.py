import numpy as np
import numpy as np
from ..qstate import Coherent
from ..qdevices import BeamSplitter,PhotonDetector
from .qkd_protocol import QKDProtocol

class COW(QKDProtocol):
    def __init__(self):
        self.first = True
        self.pdecoy = False
        self.pbit = False
        self.prev_mline = Coherent(0)

    def signal_generation(self,params):
        alpha = params['alpha']
        decoy_rate = params['decoy_rate']
        if self.first:
            decoy = np.random.rand() <= decoy_rate
            bit = np.random.rand() <= 1/2
            if bit: 
                signal =Coherent(alpha)
            else:
                signal = Coherent(0)
            self.pbit = bit
            self.pdecoy = decoy
            self.first = False
            return {'signal':signal, 'time':params['time'], 'decoy':decoy,'abits':bit}
        else:
            if self.pdecoy ^ self.pbit:
                signal =Coherent(0)
            else: 
                signal = Coherent(alpha)
            self.first = True
            return {'signal':signal, 'time':params['time'], 'decoy':self.pdecoy,'abits':self.pbit}
        
    def detection(self,params):
        if params['dark_count'][0]:
            return {'d_detector':1,'m0_detector':0,'m1_detector':0,'time':params['time']}
        if params['dark_count'][1]:
            return {'d_detector':0,'m0_detector':1,'m1_detector':0,'time':params['time']} 
        if params['dark_count'][2]:
            return {'d_detector':0,'m0_detector':0,'m1_detector':1,'time':params['time']} 
        received = params['received']
        transmitivity = params['transmitivity']

        dmlines = BeamSplitter(transmitivity).transmit(received)
        data_line = dmlines[0]
        monitor_line = dmlines[1]
        m_machzender = BeamSplitter(0.5).transmit(monitor_line)
        inst_line = m_machzender[0]
        delayed_line = m_machzender[1]

        pre_measure_mlines = BeamSplitter(0.5).transmit(np.array([self.prev_mline,inst_line]))
        d_detector = PhotonDetector().measure(data_line)
        m0_detector = PhotonDetector().measure(pre_measure_mlines[0])
        m1_detector = PhotonDetector().measure(pre_measure_mlines[1])
        self.prev_mline = delayed_line
        
        return {'d_detector':d_detector, 'm0_detector' : m0_detector, 'm1_detector':m1_detector, 'time':params['time']}

    def sift(self,aparams, bparams):
        #TODO: visibility
        decoy = aparams['decoy'][::2]
        abits = aparams['abits'][::2]
        d_detector = bparams['d_detector']
        num_key_bits = np.size(decoy) - np.sum(decoy)
        alice_key = np.empty(num_key_bits) 
        bob_key = np.empty(num_key_bits)
        j = 0
        for _ in range(np.size(decoy)):
            if not decoy[_]:
                alice_key[j] = abits[j]
                bob_key[j]= d_detector[2*j]
                j += 1
        return {'akey':alice_key.astype(int),'bkey':bob_key.astype(int)}