from ..qstate.quantum_signal import QuantumSignal

class QuantumChannel:
    def __init__(self,params):
        self.params= params

    def transmit(self,signals:QuantumSignal): # returns the signal at the receiver
        raise NotImplementedError("Subclass of QunatumChannel transmits.")

 
