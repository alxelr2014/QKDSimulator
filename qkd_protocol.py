import numpy as np

class QKDProtocol:
    def __init__(self,):
        pass

    def signal_generation(self,):
        pass

    def param_est(self,akey, bkey,frac):
        key_size = np.size(akey)
        pub_ind = np.random.choice(key_size,(int)(key_size*frac), replace=False)
        difference = (akey != bkey)[pub_ind]
        print(akey, bkey, pub_ind, difference)
        return np.delete(akey,pub_ind), np.delete(bkey,pub_ind), np.sum(difference)/np.size(pub_ind)     

    def sift(self,):
        pass
    def run_protocol(self,num_signal):
        pass
