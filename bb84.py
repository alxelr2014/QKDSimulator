import numpy as np
from quantum_signal import *
from quantum_channel import *
from quantum_measurement import *
from qkd_protocol import *


class BB84(QKDProtocol):
    def __init__(self):
        pass

    def signal_generation(self,params):
        num_signal = params['num_signal']
        intensities = np.array([params['alpha'], params['mu']])
        decoy_rate = params['decoy_rate']

        decoy = np.random.rand(num_signal) <= decoy_rate
        pol_basis = np.random.rand(num_signal) <= 1/2
        polarization = np.random.rand(num_signal) <= 1/2
        phi = np.random.rand(num_signal)*2*np.pi
        signals = np.empty(num_signal,dtype=QuantumSignal)
        for _ in range(num_signal):
            if pol_basis[_]:
                if polarization[_]:
                    pol_type = PolarizeType.A
                else:
                    pol_type = PolarizeType.D
            else:
                if polarization[_]:
                    pol_type = PolarizeType.V
                else:
                    pol_type = PolarizeType.H
            signals[_] = Coherent(np.exp(1j*phi[_])*intensities[(int) (decoy[_])],pol_type)          
        return {'signals':signals, 'decoy':decoy,'apol_basis':pol_basis, 'apolarization':polarization}
    

    def detection(self,params):
        received= params['received']
        num_signal = params['num_signal']
        counter = np.zeros(num_signal,dtype=object)
        bpol_basis = np.random.rand(num_signal) <= 1/2
        for _ in range(num_signal):
            if not bpol_basis[_]:
                mpol = PolarizeType.H
            else:
                mpol = PolarizeType.D
            counter[_] = PhotonCounter().measure(received[_],Polarization(mpol))
        return {'bcounter':counter,'bpol_basis':bpol_basis}
    
    def sift(self,aparams,bparams):
        num_signal = aparams['num_signal']
        decoy = aparams['decoy']
        apol_basis = aparams['apol_basis']
        apolarization = aparams['apolarization']
        bcounter = bparams['bcounter']
        bpol_basis =bparams['bpol_basis']

        alice_key = np.empty(num_signal)
        bob_key = np.empty(num_signal)
        j =0 
        for _ in range(num_signal):
            if not decoy[_]:
                if apol_basis[_] == bpol_basis[_]:
                    alice_key[j] = apolarization[_]
                    bob_key[j] = bcounter[_][1] > 0
                    j += 1
        return {'akey': alice_key[:j], 'bkey': bob_key[:j]}
    

    def param_est(self,params):
        return super().param_est(params)


    def run_protocol(self,num_signal,frac):
        decoy = np.random.rand(num_signal) <= self.decoy_rate
        pol_basis = np.random.rand(num_signal) <= 1/2
        polarization = np.random.rand(num_signal) <= 1/2
        phi = np.random.rand(num_signal)*2*np.pi
        signals = self.signal_generation(decoy,pol_basis,polarization,phi,num_signal)

        seq_trans = np.vectorize(self.qchannel.transmit)
        received = seq_trans(signals)

        # print(decoy.astype(int))
        # print(pol_basis.astype(int))
        # print(polarization.astype(int))
        # print(phi.astype(float))
        # print(mpol_basis.astype(int))
        # print(counter)

        alice_key, bob_key = self.sift(decoy,pol_basis,polarization,counter,mpol_basis,num_signal)

        # print(alice_key.astype(int))
        # print(bob_key.astype(int))
        return self.param_est(alice_key,bob_key,frac)

    # def param_est(self,):
    #     pass