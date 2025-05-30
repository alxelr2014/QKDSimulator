from .quantum_measurement import QuantumMeasurement,event_select
from ..qstate.quantum_signal import QuantumSignal
from ..qstate.polarization import Polarization
import numpy as np

class PhotonDetector(QuantumMeasurement):
    def __init__(self):
        super().__init__({})
    def measure(self,signal:QuantumSignal, pol: Polarization = None):
        if pol == None:
            return event_select(
                prob_dist= signal.probn_photon(),
                fevent=lambda x: 0 if x == 0 else 1,
                max_limit= 2)
        
        else:
            plist = signal.prob00_detection(pol)
            probs = [plist[0]*plist[1], (1-plist[0])*plist[1],(1-plist[1])*plist[0],(1-plist[0])*(1-plist[1])]
            acum = np.add.accumulate(probs)
            mapping = [(0,0), (0,1), (1,0),(1,1)]
            return event_select(
                prob_dist= lambda x: acum[x] if x <=3 else 0,
                fevent=lambda x:mapping[x] if x <= 3 else mapping[3],
                max_limit=6
            )
            
            # l = float(np.random.rand())
            # if l > acum[1]:
            #     if l > acum[2]:
            #         return 1,1
            #     return 0,1
            # else:
            #     if l > acum[0]:
            #         return 1,0
            #     return 0,0
                
