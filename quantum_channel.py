import numpy as np
from quantum_signal import *
from quantum_channel import *

class QuantumChannel:
    def __init__(self,params):
        self.params= params

    def transmit(self,signals:QuantumSignal): # returns the signal at the receiver
        raise NotImplementedError("Subclass of QunatumChannel transmits.")

class Fiber(QuantumChannel):
    def transmit(self, signals):
        return signals
    
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

        return np.array([Coherent(alpha_out), QuantumSignal(Coherent,beta_out)])