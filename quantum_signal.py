from enum import Enum, auto
import numpy as np

class SignalType(Enum):
    COHERENT = auto()


class QuantumSignal:
    def __init__(self,type,param):
        self.type =type
        self.param = param

    def get_type(self):
        return self.type
    def get_param(self,key):
        return self.param[key]
    
    def inner_product(self,state):
        pass

    def inner_product0(self):
        pass

class Coherent(QuantumSignal):
    def __init__(self, alpha):
        param = {"alpha":alpha}
        super().__init__(SignalType.COHERENT, param)
    
    def inner_product(self,state):
        pass
    def inner_product0(self):
        return np.exp(-1/2*(self.param['alpha'])**2)
