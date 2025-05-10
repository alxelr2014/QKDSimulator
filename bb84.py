import numpy as np
from quantum_signal import *
from quantum_channel import *
from quantum_measurement import *
from qkd_protocol import *


class BB84(QKDProtocol):
    def __init__(self,params):
        self.alpha = params['alpha']
        self.decoy_rate = params['decoy_rate']
        self.qchannel = params['qchannel']
        self.transmitivity = params['transmitivity']

    def run_protocol(self,params):
        num_signal = params['num_signal']
        decoy = np.random.rand(num_signal) <= self.decoy_rate
        bits = np.random.rand(num_signal) <= 1/2
        signals = self.signal_generation(decoy,bits,num_signal)
        seq_trans = np.vectorize(self.qchannel.transmit)
        received = seq_trans(signals)

        d_counter = np.zeros(num_signal)
        m0_counter = np.zeros(num_signal)
        m1_counter = np.zeros(num_signal)
        prev_mline = Coherent(0)
        for _ in range(num_signal):
            dmlines = coh_BeamSplitter(self.transmitivity).transmit(received[_])
            data_line = dmlines[0]
            monitor_line = dmlines[1]
            d_counter[_] = SinglePhotonMeasurement().measure(data_line)
            pre_measure_mlines = coh_MachZender(0).transmit(np.array([prev_mline,monitor_line]))
            m0_counter[_] = SinglePhotonMeasurement().measure(pre_measure_mlines[0])
            m1_counter[_] = SinglePhotonMeasurement().measure(pre_measure_mlines[1])
            prev_mline = monitor_line
        
        return self.sift_pe(decoy,bits,d_counter,m0_counter,m1_counter)

    def sift_pe(decoy,bits,d_counter,m0_counter,m1_counter):
        pass

    def signal_generation(self,decoy,bits,num_signal):
        signals = np.empty(2*num_signal,dtype=QuantumSignal)
        for _ in range(num_signal):
            if bits[_]: 
                signals[2*_] =QuantumSignal(SignalType.COHERENT,self.alpha)
            else:
                signals[2*_] = QuantumSignal(SignalType.COHERENT,0)
            if decoy[_]:
                signals[2*_+1] =QuantumSignal(SignalType.COHERENT,0)
            else: 
                signals[2*_ + 1] = QuantumSignal(SignalType.COHERENT,self.alpha)
            
        return signals
    