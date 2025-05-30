import numpy as np
from ..qstate.quantum_signal import QuantumSignal,SignalType
from ..qstate.coherent import Coherent
from .quantum_channel import QuantumChannel
    

class coh_MachZender(QuantumChannel):
    def __init__(self, phase_delay):
        params = {'phase_delay' : phase_delay}
        super().__init__(params)

    def transmit(self, signals:QuantumSignal):
        if not isinstance(signals,np.ndarray) and isinstance(signals,QuantumSignal):
            signals = np.array([signals,Coherent(0)])
        if isinstance(signals,np.ndarray) and np.size(signals) == 1:
            signals =np.append(signals,Coherent(0))
        if not isinstance(signals,np.ndarray) or np.size(signals) != 2:
            raise TypeError("coh_MachZender Signals are not QuantumSignals or an array of QuantumSignals.")
        if signals[0].get_type() != SignalType.COHERENT or signals[1].get_type() != SignalType.COHERENT:
            raise TypeError("coh_MachZender Signals are not coherent signals.")
        
        alpha = signals[0].get_param('alpha')
        beta = signals[1].get_param('alpha')
        ephi = np.exp(1j*(self.params['phase_delay']))


        #TODO: check formulea
        alpha_out = 1/2* ((ephi - 1)*alpha - 1j*(1+ephi)*beta)
        beta_out = 1/2* ((1-ephi)*beta - 1j*(1+ephi)*alpha)

        return np.array([Coherent(alpha_out), Coherent(beta_out)])