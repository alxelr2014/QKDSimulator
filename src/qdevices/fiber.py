import numpy as np
from ..qstate.quantum_signal import QuantumSignal,SignalType
from ..qstate.coherent import Coherent
from .quantum_channel import QuantumChannel

class Fiber(QuantumChannel):
    def __init__(self,params):
        super().__init__(params)

    def transmit(self, signal):
        if not isinstance(signal,np.ndarray) and not isinstance(signal,QuantumSignal):
            raise TypeError("Fiber input are not signal.")
        if isinstance(signal,np.ndarray):
            if np.size(signal) == 1 :
                signal = signal[0]
            else:
                raise TypeError("More than one signal is present in the fiber.")
        if isinstance(signal,QuantumSignal) and  signal.get_type() != SignalType.COHERENT:
            raise TypeError("Fiber signal is not a coherent signal.")
        
        transmitivity = np.exp(-self.params['gamma'] * self.params['length'])
        out_alpha = np.sqrt(transmitivity)* signal.get_param('alpha')

        return Coherent(out_alpha,signal.get_param('polarization'))
