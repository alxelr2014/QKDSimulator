
from .polarization import PolarizeType,Polarization
from .quantum_signal import QuantumSignal,SignalType
import numpy as np



class Coherent(QuantumSignal):
    def __init__(self, alpha, pol = PolarizeType.H):
        param = {'alpha':alpha, 'polarization': Polarization(pol)}
        super().__init__(SignalType.COHERENT, param)

    
    def probn_photon(self): # measure in the same polarization
        def prob_dist(n):
            return poisson(n,np.abs(self.param['alpha'])**2)
        return prob_dist

    def prob00_detection(self,mpol:Polarization):
        v1 = self.param['polarization'].pol[0]
        v2 = self.param['polarization'].pol[1]
        alpha = self.param['alpha']

        u1 = mpol.pol[0]
        u2 = mpol.pol[1]

        amp1 =np.abs(u1*np.conj(v1)*alpha + u2*np.conj(v2)*alpha)**2
        amp2 = np.abs(u2*v1*alpha - u1*v2*alpha)**2
        return [poisson(0, amp1), poisson(0, amp2)] 
    
    def probnm_photon(self,mpol:Polarization): # measure in a different polarization
        def prob_dist(n,m):
            v1 = self.param['polarization'].pol[0]
            v2 = self.param['polarization'].pol[1]
            alpha = self.param['alpha']

            u1 = mpol.pol[0]
            u2 = mpol.pol[1]

            amp1 =np.abs(u1*np.conj(v1)*alpha + u2*np.conj(v2)*alpha)**2
            amp2 = np.abs(u2*v1*alpha - u1*v2*alpha)**2
            return poisson(n, amp1) * poisson(m, amp2)
        return prob_dist

def poisson(n,mu):
    if n == 0:
        return np.exp(-mu)
    else:
        return (mu/n) * poisson(n-1,mu)
