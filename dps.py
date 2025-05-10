import numpy as np
from quantum_signal import *
from quantum_channel import *
from quantum_measurement import *
from qkd_protocol import *


class DPS(QKDProtocol):
    def __init__(self,params):
        self.alpha = params['alpha']
        self.qchannel = params['qchannel']

    def run_protocol(self,params):
        num_signal = params['num_signal']
        bits = np.random.rand(num_signal) <= 1/2
        signals = self.signal_generation(bits,num_signal)
        seq_trans = np.vectorize(self.qchannel.transmit)
        received = seq_trans(signals)


        m0_counter = np.zeros(num_signal)
        m1_counter = np.zeros(num_signal)
        prev_del_line = Coherent(0)
        for _ in range(num_signal):
            cd_lines = coh_BeamSplitter(0.5).transmit(received[_])
            curr_line = cd_lines[0]
            del_lin = cd_lines[1]
            measure_lines = coh_BeamSplitter(0.5).transmit(np.array([curr_line,prev_del_line]))
            m0_counter[_] = SinglePhotonMeasurement().measure(measure_lines[0])
            m1_counter[_] = SinglePhotonMeasurement().measure(measure_lines[1])
            prev_del_line = del_lin
        
        alice_key, bob_key = self.sift(bits,m0_counter,m1_counter)
        print(bits.astype(int))
        print(m0_counter.astype(int))
        print(m1_counter.astype(int))
        print(alice_key.astype(int))
        print(bob_key.astype(int))
        parameters = self.param_est()

        return alice_key,bob_key,parameters

    def sift(self,bits,m0_counter,m1_counter):
        bob_message = np.logical_or(m0_counter, m1_counter)
        # note the the first clicks are dont cares
        # TODO: is that true?

        # print(m0_counter.astype(int))
        # print(m1_counter.astype(int))
        # print(bits.astype(int))
        num_clicks = bob_message.sum()-bob_message[0]
        if num_clicks <= 0:
            raise RuntimeError("DPS protocol produced no keys. Aborted!")
        
            
        alice_key = np.full(num_clicks,-1)
        bob_key = np.full(num_clicks,-1)
        # print(bob_message.astype(int))
        # print(bob_message.sum())
        key_ind = 0
        for _ in range(1,len(bob_message)):
            if bob_message[_]:
                alice_key[key_ind] = 1- (bits[_] ^ bits[_-1])
                bob_key[key_ind] = 1 - m0_counter[_]
                key_ind += 1
        return alice_key,bob_key
 
    def param_est(self,):
        pass


    def signal_generation(self,bits,num_signal):
        signals = np.empty(num_signal,dtype=QuantumSignal)
        for _ in range(num_signal):
            signals[_] =Coherent((-1)**(bits[_])*self.alpha)
        return signals


s = DPS({'alpha':0.5,'qchannel':Fiber({})})
s.run_protocol(params={'num_signal':200})