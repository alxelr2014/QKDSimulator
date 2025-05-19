import numpy as np
from quantum_signal import *
from quantum_channel import *
from quantum_measurement import *
from qkd_protocol import *


class BB84(QKDProtocol):
    def __init__(self):
        pass

    def signal_generation(self,params):
        intensities = np.array([params['alpha'], params['mu']])
        decoy_rate = params['decoy_rate']

        decoy = np.random.rand() <= decoy_rate
        pol_basis = np.random.rand() <= 1/2
        polarization = np.random.rand() <= 1/2
        phi = np.random.rand()*2*np.pi
        if pol_basis:
            if polarization:
                pol_type = PolarizeType.A
            else:
                pol_type = PolarizeType.D
        else:
            if polarization:
                pol_type = PolarizeType.V
            else:
                pol_type = PolarizeType.H
        signal = Coherent(np.exp(1j*phi)*intensities[(int) (decoy)],pol_type)          
        return {'signal':signal, 'decoy':decoy,'apol_basis':pol_basis, 'apolarization':polarization, 'time' : params['time']}
    

    def detection(self,params):
        if params['dark_count'][0]:
            return {'bdetector':(1,0),'bpol_basis':-1,'time':params['time']}
        received= params['received']
        bpol_basis = np.random.rand() <= 1/2
        if not bpol_basis:
            mpol = PolarizeType.H
        else:
            mpol = PolarizeType.D
        detector = PhotonDetector().measure(received,Polarization(mpol))
        return {'bdetector':detector,'bpol_basis':bpol_basis, 'time' : params['time']}
    
    def sift(self,aparams,bparams):
        decoy = aparams['decoy']
        num_signal = np.size(decoy)
        apol_basis = aparams['apol_basis']
        apolarization = aparams['apolarization']
        bdetector = bparams['bdetector']
        bpol_basis =bparams['bpol_basis']

        alice_key = np.empty(num_signal)
        bob_key = np.empty(num_signal)
        j =0 
        for _ in range(num_signal):
            if not decoy[_]:
                if apol_basis[_] == bpol_basis[_]:
                    alice_key[j] = apolarization[_]
                    bob_key[j] = bdetector[_][1] == 1
                    j += 1
        return {'akey': alice_key[:j].astype(int), 'bkey': bob_key[:j].astype(int)}
    

    def param_est(self,params):
        return super().param_est(params)