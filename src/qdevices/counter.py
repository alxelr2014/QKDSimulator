
from .quantum_measurement import QuantumMeasurement
from ..qstate.quantum_signal import QuantumSignal
from ..qstate.polarization import Polarization
import numpy as np


class PhotonCounter(QuantumMeasurement):
    def __init__(self):
        super().__init__({})
    def measure(self,signal:QuantumSignal, pol: Polarization = None):
        if pol == None:
            p = signal.prob_nphoton()
            l = float(np.random.rand())
            n = -1
            s = 0
            while l > s:
                n+= 1
                s += p(n)
                if n > 1000:
                    break
            return n
        else:
            p = signal.probnm_photon(pol)
            l = float(np.random.rand())
            n = 0
            m = 0
            s = p(n,m)
            while l > s:
                if n == 0:
                    n = m +1
                    m = 0
                else:
                    n -= 1
                    m += 1
                s += p(n,m)
                if n > 50:
                    return n,m
            return n,m

