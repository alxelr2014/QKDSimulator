import numpy as np
from quantum_signal import *
from quantum_channel import *
from quantum_measurement import *
from qkd_protocol import *


class COW(QKDProtocol):
    def __init__(self):
        pass

    def signal_generation(self,params):
        num_signal = params['num_signal']
        alpha = params['alpha']
        decoy_rate = params['decoy_rate']
        decoy = np.random.rand(num_signal) <= decoy_rate
        bits = np.random.rand(num_signal) <= 1/2
        signals = np.empty(2*num_signal,dtype=QuantumSignal)
        for _ in range(num_signal):
            if bits[_]: 
                signals[2*_] =Coherent(alpha)
            else:
                signals[2*_] = Coherent(0)
            if decoy[_] ^ bits[_]:
                signals[2*_+1] =Coherent(0)
            else: 
                signals[2*_ + 1] = Coherent(alpha)
        return {'signals':signals, 'decoy':decoy,'abits':bits}

    def detection(self,params):
        num_signal = params['num_signal']
        received = params['received']
        transmitivity = params['transmitivity']

        d_counter = np.zeros(2*num_signal)
        m0_counter = np.zeros(2*num_signal)
        m1_counter = np.zeros(2*num_signal)
        prev_mline = Coherent(0)
        for _ in range(2*num_signal):
            dmlines = coh_BeamSplitter(transmitivity).transmit(received[_])
            data_line = dmlines[0]
            monitor_line = dmlines[1]
            m_machzender = coh_BeamSplitter(0.5).transmit(monitor_line)
            inst_line = m_machzender[0]
            delayed_line = m_machzender[1]

            pre_measure_mlines = coh_BeamSplitter(0.5).transmit(np.array([prev_mline,inst_line]))
            d_counter[_] = PhotonDetector().measure(data_line)
            m0_counter[_] = PhotonDetector().measure(pre_measure_mlines[0])
            m1_counter[_] = PhotonDetector().measure(pre_measure_mlines[1])
            prev_mline = delayed_line
        
        return {'d_counter':d_counter, 'm0_counter' : m0_counter, 'm1_counter':m1_counter}

    def sift(self,aparams, bparams):
        decoy = aparams['decoy']
        abits = aparams['abits']
        d_counter = bparams['d_counter']
        num_key_bits = np.size(decoy) - np.sum(decoy)
        alice_key = np.empty(num_key_bits) 
        bob_key = np.empty(num_key_bits)
        j = 0
        for _ in range(np.size(decoy)):
            if not decoy[_]:
                alice_key[j] = abits[j]
                bob_key[j]= d_counter[2*j]
                j += 1
        return {'akey':alice_key,'bkey':bob_key}

    def run_protocol(self,num_signal,frac):

        signals = self.signal_generation(decoy,bits,num_signal)
  

        
        
        # print(decoy.astype(int))
        # print(bits.astype(int))
        # print(d_counter.astype(int))
        # print(m0_counter.astype(int))
        # print(m1_counter.astype(int))

        alice_key,bob_key = self.sift(decoy,bits,d_counter)
        # print(alice_key.astype(int))
        # print(bob_key.astype(int))
        # print(np.logical_xor(alice_key,bob_key).astype(int))
        # print(np.sum(np.logical_xor(alice_key,bob_key)))
        return self.param_est(alice_key,bob_key,frac)





    # def param_est(self,decoy,bits,d_counter,m1_counter):
    #     return 0

