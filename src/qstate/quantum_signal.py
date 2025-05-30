from enum import Enum, auto
import numpy as np
from .polarization import Polarization


class SignalType(Enum):
    COHERENT = auto()


class QuantumSignal:
    def __init__(self,type : SignalType,param : dict):
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
