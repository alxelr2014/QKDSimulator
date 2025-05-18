import numpy as np
from quantum_signal import *
from quantum_channel import *
from quantum_measurement import *
from qkd_protocol import *


class DPS(QKDProtocol):
    def __init__(self,):
        pass

    def signal_generation(self,params):
        num_signal = params['num_signal']
        alpha = params['alpha']
        bits = np.random.rand(num_signal) <= 1/2
        signals = np.empty(num_signal,dtype=QuantumSignal)
        for _ in range(num_signal):
            signals[_] =Coherent((-1)**(bits[_])*alpha)
        return {'signals':signals,'abits':bits}

    def detection(self,params):
        received= params['received']
        num_signal = params['num_signal']
        m0_counter = np.zeros(num_signal)
        m1_counter = np.zeros(num_signal)
        prev_del_line = Coherent(0)
        for _ in range(num_signal):
            cd_lines = coh_BeamSplitter(0.5).transmit(received[_])
            curr_line = cd_lines[0]
            del_lin = cd_lines[1]
            measure_lines = coh_BeamSplitter(0.5).transmit(np.array([curr_line,prev_del_line]))
            m0_counter[_] = PhotonDetector().measure(measure_lines[0])
            m1_counter[_] = PhotonDetector().measure(measure_lines[1])
            prev_del_line = del_lin
        return {'m0_counter' : m0_counter, 'm1_counter': m1_counter}

    def run_protocol(self,num_signal,frac):
        
        seq_trans = np.vectorize(self.qchannel.transmit)
        received = seq_trans(signals)


        
        alice_key, bob_key = self.sift(bits,m0_counter,m1_counter)

        # print(bits.astype(int))
        # print(m0_counter.astype(int))
        # print(m1_counter.astype(int))
        # print(alice_key.astype(int))
        # print(bob_key.astype(int))

        return self.param_est(alice_key,bob_key,frac)

    def sift(self,aparams,bparams):
        abits = aparams['abits']
        m0_counter = bparams['m0_counter']
        m1_counter = bparams['m1_counter']
        bob_message = np.logical_or(m0_counter, m1_counter)
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
                bob_key[key_ind] = 1 - m0_counter[_]
                key_ind += 1

        return {'akey': alice_key, 'bkey': bob_key}
    
    
    def param_est(self,params):
        return super().param_est(params)
 
    # def param_est(self,):
    #     pass

