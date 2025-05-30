from ..qstate.quantum_signal import QuantumSignal
from numpy.random import rand

class QuantumMeasurement:
    def __init__(self,params):
        self.params = params
    
    def measure(self,signal:QuantumSignal): # returns the signal at the receiver
        raise NotImplementedError("Subclass of QuantumMeasurement measures.")



def event_select(prob_dist,fevent, max_limit = 1000):
    '''
        Randomly chooses an event, by first choosing a Natural number 
        with respect to the given probability distribution and then applying
        the given (bijective) function to get the event.
        prob_dist := probability distribution on Naturals
        fevent := a function from Naturals to the events
        max_limit := the maximum that range of prob_dist should go. (otherwise might loop infinitely)
    '''
    p= float(rand())
    n = -1
    s = 0
    while p > s:
            n+= 1
            s += prob_dist(n)
            if n > max_limit:
                break
    return fevent(n)

    
