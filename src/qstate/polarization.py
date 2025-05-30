from enum import Enum, auto
import numpy as np

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
        elif isinstance(pol, Polarization):
            self.pol = pol.pol
        else:
            self.pol = np.array([1,0])
        