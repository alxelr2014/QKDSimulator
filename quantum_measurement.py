import numpy as np
from quantum_signal import *
from quantum_channel import *

class QuantumMeasurement:
    def __init__(self,params):
        self.params = params
    
    def measure(self,signal:QuantumSignal): # returns the signal at the receiver
        raise NotImplementedError("Subclass of QuantumMeasurement measures.")

class PhotonDetector(QuantumMeasurement):
    def __init__(self):
        super().__init__({})
    def measure(self,signal:QuantumSignal):
        p = signal.probn_photon()
        l = float(np.random.rand())
        return l > p(0)
    
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
# for i in range(3):
#     print(PhotonCounter().measure(Coherent(4,PolarizeType.D), Polarization(PolarizeType.A)))
# def triflatify(n):
#     k = (int)(np.floor(-1/2 + np.sqrt(1/4 + 2*n)))
#     t = ((k)*(k+1))//2
#     m = n - t
#     return k-m,m




