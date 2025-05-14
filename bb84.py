import numpy as np
from quantum_signal import *
from quantum_channel import *
from quantum_measurement import *
from qkd_protocol import *


class BB84(QKDProtocol):
    def __init__(self,params):
        self.intensities = np.array([params['alpha'], params['mu']])
        self.decoy_rate = params['decoy_rate']
        self.qchannel = params['qchannel']

    def run_protocol(self,params):
        num_signal = params['num_signal']
        decoy = np.random.rand(num_signal) <= self.decoy_rate
        pol_basis = np.random.rand(num_signal) <= 1/2
        polarization = np.random.rand(num_signal) <= 1/2
        phi = np.random.rand(num_signal)*2*np.pi
        signals = self.signal_generation(decoy,pol_basis,polarization,phi,num_signal)

        seq_trans = np.vectorize(self.qchannel.transmit)
        received = seq_trans(signals)

        counter = np.zeros(num_signal,dtype=object)
        mpol_basis = np.random.rand(num_signal) <= 1/2
        for _ in range(num_signal):
            if mpol_basis[_]:
                mpol = PolarizeType.H
            else:
                mpol = PolarizeType.D
            counter[_] = PhotonCounter().measure(received[_],Polarization(mpol))
        
        # print(decoy.astype(int))
        # print(pol_basis.astype(int))
        # print(polarization.astype(int))
        # print(phi.astype(float))
        # print(mpol_basis.astype(int))
        # print(counter)

        alice_key, bob_key = self.sift(decoy,pol_basis,polarization,counter,mpol_basis,num_signal)

        # print(alice_key.astype(int))
        # print(bob_key.astype(int))
        parameters = self.param_est()
        return alice_key,bob_key,parameters

    def sift(self,decoy,pol_basis,polarization,counter,mpol_basis,num_signal):
        alice_key = np.empty(num_signal)
        bob_key = np.empty(num_signal)
        j =0 
        for _ in range(num_signal):
            if not decoy[_]:
                if pol_basis[_] == mpol_basis[_]:
                    alice_key[j] = polarization[_]
                    bob_key[j] = counter[_][1] > 0
                    j += 1
        return alice_key[:j],bob_key[:j]

    def param_est(self,):
        return 0

    def signal_generation(self,decoy,pol_basis,pol,phi,num_signal):
        signals = np.empty(num_signal,dtype=QuantumSignal)
        for _ in range(num_signal):
            if pol_basis[_]:
                if pol[_]:
                    pol_type = PolarizeType.A
                else:
                    pol_type = PolarizeType.D
            else:
                if pol[_]:
                    pol_type = PolarizeType.V
                else:
                    pol_type = PolarizeType.H
            signals[_] = Coherent(np.exp(1j*phi[_])*self.intensities[(int) (decoy[_])],pol_type)          
        return signals