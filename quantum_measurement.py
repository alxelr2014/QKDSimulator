import numpy as np
from quantum_signal import *
from quantum_channel import *

class QuantumMeasurement:
    def __init__(self,params):
        self.params = params
    
    def measure(self,signal:QuantumSignal): # returns the signal at the receiver
        raise NotImplementedError("Subclass of QuantumMeasurement measures.")

class SinglePhotonMeasurement(QuantumMeasurement):
    def measure(self,signal:QuantumSignal):
        P0 = signal.inner_product0()
        l = np.random.rand()[0]
        return l > P0