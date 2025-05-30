import numpy as np
from ..qstate.quantum_signal import QuantumSignal,SignalType
from ..qstate.coherent import Coherent
from .quantum_channel import QuantumChannel


   
class coh_BeamSplitter(QuantumChannel):
    def __init__(self, transmitivity):
        params = {'transmitivity' : transmitivity}
        super().__init__(params)

    def transmit(self,signals:QuantumSignal):
        if not isinstance(signals,np.ndarray) and isinstance(signals,QuantumSignal):
            signals = np.array([signals,Coherent(0)])
        if isinstance(signals,np.ndarray) and np.size(signals) == 1:
            signals =np.append(signals,Coherent(0))
        if not isinstance(signals,np.ndarray) or np.size(signals) != 2:
            raise TypeError("coh_Beamsplitter Signals are not QuantumSignals or an array of QuantumSignals.")
        if signals[0].get_type() != SignalType.COHERENT or signals[1].get_type() != SignalType.COHERENT:
            raise TypeError("coh_Beamsplitter Signals are not coherent signals.")
        alpha = signals[0].get_param('alpha')
        beta = signals[1].get_param('alpha')
        eta = (self.params['transmitivity'])

        #TODO: check formulea
        alpha_out = np.sqrt(eta)*alpha - 1j*beta*np.sqrt(1-eta)
        beta_out = -1j* np.sqrt(1-eta)*alpha +beta*np.sqrt(eta)

        return np.array([Coherent(alpha_out), Coherent(beta_out)])
        