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

    def sift_darkcount(self,alice_data,bob_data,channel_data):
        delay = channel_data['delay']
        margin = channel_data['margin']
        aparams = {}
        bparams = {}
        max_size = np.size(alice_data)
        for key, value in alice_data[0].items():
            if key != 'time':
                aparams[key] = np.empty(max_size,dtype=type(value))
        for key, value in bob_data[0].items():
            if key != 'time':
                bparams[key] = np.empty(max_size,dtype=type(value))

        pb = 0
        ind = 0
        for pa in range(len(alice_data)):
            while bob_data[pb]['time'] - alice_data[pa]['time'] < 0:
                pb += 1
            if bob_data[pb]['time'] - alice_data[pa]['time'] < delay + margin:
                for key in aparams.keys():
                    aparams[key][ind] = alice_data[pa][key]
                for key in bparams.keys():
                    bparams[key][ind] = bob_data[pb][key]
                ind += 1
        
        for key in aparams.keys():
            aparams[key] = aparams[key][0:ind]
        for key in bparams.keys():
            bparams[key] = bparams[key][0:ind]
        return aparams,bparams

                


    def param_est(self,params):
        akey = params['akey']
        bkey = params['bkey']
        frac = params['frac']
        key_size = np.size(akey)
        pub_ind = np.random.choice(key_size,(int)(key_size*frac), replace=False)
        difference = (akey != bkey)[pub_ind]
        return {'akey': np.delete(akey,pub_ind), 'bkey':np.delete(bkey,pub_ind), 
                'qber':np.sum(difference)/np.size(pub_ind)}     

