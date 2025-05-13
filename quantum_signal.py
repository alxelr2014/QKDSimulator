from enum import Enum, auto
import numpy as np

class SignalType(Enum):
    COHERENT = auto()

class PolarizeType(Enum):
    H = auto()
    V = auto()
    D = auto()
    A = auto()

class Polarization:    
    def __init__(self,pol):
        if isinstance(pol,np.ndarray):
            self.pol = pol
        elif isinstance(pol,PolarizeType):
            if pol == PolarizeType.H:
                self.pol = np.array([1,0])
            elif pol == PolarizeType.V:
                self.pol = np.array([0,1])
            elif pol == PolarizeType.D:
                self.pol = np.array([1/np.sqrt(2),1/np.sqrt(2)])
            elif pol == PolarizeType.A:
                self.pol = np.array([1/np.sqrt(2),-1/np.sqrt(2)])
            else:
                self.pol = np.array([1,0])
        else:
            self.pol = np.array([1,0])

class QuantumSignal:
    def __init__(self,type,param):
        self.type =type
        self.param = param

    def get_type(self):
        return self.type
    def get_param(self,key):
        return self.param[key]
    
    def probn_photon(self):
        pass

    def probnm_photon(self,mpol:Polarization):
        pass

class Coherent(QuantumSignal):
    def __init__(self, alpha, pol = Polarization(PolarizeType.H)):
        param = {'alpha':alpha, 'polarization': Polarization(pol)}
        super().__init__(SignalType.COHERENT, param)

    
    def probn_photon(self): # measure in the same polarization
        def prob_dist(n):
            return poisson(n,np.abs(self.param['alpha'])**2)
        return prob_dist
        
    
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
