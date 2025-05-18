import numpy as np

class QKDProtocol:
    def __init__(self,):
        pass

    def signal_generation(self,):
        pass

    def detection(self,):
        pass

    def sift(self,):
        pass

    def param_est(self,params):
        akey = params['akey']
        bkey = params['bkey']
        frac = params['frac']
        key_size = np.size(akey)
        pub_ind = np.random.choice(key_size,(int)(key_size*frac), replace=False)
        difference = (akey != bkey)[pub_ind]
        return {'akey': np.delete(akey,pub_ind), 'bkey':np.delete(bkey,pub_ind), 
                'qber':np.sum(difference)/np.size(pub_ind)}     

