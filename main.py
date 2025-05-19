from bb84 import *
from cow import *
from dps import *
from simulation import *

import numpy as np
import matplotlib.pyplot as plt
from functools import partial
from multiprocessing import Pool
from Crypto.Random import get_random_bytes
from Crypto.Hash import HMAC, SHA256

hex_hash_key =    get_random_bytes(16)
def secure_hash_using_hmac( data):
    h = HMAC.new(hex_hash_key, digestmod=SHA256)
    h.update(data)
    return h.hexdigest()

def bytify(bitvec):
    return secure_hash_using_hmac(bytes(np.packbits(bitvec)))

def print_result(pe,n,str):
    # print("############## "+str+" ##############")
    # print('Alice\'s Key: ', (pe['akey']))
    # print('Bob\'s Key:   ', (pe['bkey']))
    # if 'qber' in pe:
    #     print('QBER: ', pe['qber'])
    # print('Rate: ', np.size(pe['akey'])/n)
    # print('Number of errors: ', np.sum(np.logical_xor(pe['akey'],pe['bkey'])))
    # print("############################")
    return np.size(pe['akey'])/n

def dic_update(dic,key,val):
    for k in dic.keys():
        if key == k:
            dic[k] = val
        if isinstance(dic[k], dict):
            dic[k] = dic_update(dic[k],key,val)
    return dic

def simulate_vs(v,param,label):
    param = dic_update(param,label,v)
    s = Simulation(protocol=param['protocol'],
    qchannel= param['qchannel'](param['qchannel_params']),
    signal_params=param['signal_params'],
    detect_params=param['detect_params'],
    num_detectors=param['num_detectors'],
    darkcount_rate=param['darkcount_rate'],
    clk=param['clk'],
    delay=param['channel_data']['delay'],
    post_proc=param['post_proc'],
    num_signal=param['num_signal'],
    debug=param['debug'])

    s.schedule_event(Event(0,s.start_event,'Start'))
    alice_data, bob_data = s.run_qkd()
    keys = s.sifting(alice_data,bob_data,param['channel_data'])
    pe = s.param_est(keys | param['est_params'])
    param_rate = print_result(pe , param['num_signal'], 'Parameter Estimation')

    ir = s.info_recon(pe)
    print_result(ir , param['num_signal'], 'Information Reconcilliation' )

    pa = s.priv_amp(ir | param['priv_params'])
    priv_rate = print_result(pa , param['num_signal'], 'Privacy Amplification')
    return param_rate, priv_rate

def plot_rate_vs(params,var,var_range,num_proc,filename = 'test'):
    param_rate = np.empty(params['num_simulations'],dtype=np.ndarray)
    priv_rate = np.empty(params['num_simulations'],dtype=np.ndarray)
    for _ in range(params['num_simulations']):
        with Pool(num_proc) as p:
            rates = p.map(partial(simulate_vs, param=params,label=var), var_range)
        new_est_rate, new_amp_rate = zip(*rates)
        param_rate[_] =np.array(new_est_rate)
        priv_rate[_] = np.array(new_amp_rate)
    
    print(priv_rate)
    param_rate = np.average(param_rate,axis=0)
    priv_rate = np.average(priv_rate, axis=0)
    print(priv_rate)
        
    fig, ax = plt.subplots()
    ax.plot(var_range, param_rate, label = 'Param Est Rate')
    ax.plot(var_range,priv_rate, label = 'Priv Amp Rate')

    ax.set(xlabel=var, ylabel='Rates',
        title='Rates vs ' + var)
    ax.set_ylim(0.0,0.6)
    ax.grid()
    ax.legend(loc='upper left')

    fig.savefig('./Figure/'+filename+'.png')
    plt.show()



if __name__ == "__main__":
    param = {
        'protocol' : BB84(),
        'qchannel' : Fiber,
        'qchannel_params': {'length' : 1, 'gamma' : 0.2},
        'signal_params' : {'alpha':0.3,'mu' : 0.1, 'decoy_rate':0.2},
        'detect_params' : {},
        'num_detectors' : 1,
        'darkcount_rate': 10,
        'clk' : 1,
        'channel_data': {'delay' : 1e-2, 'margin' : 1e-3},
        'est_params': {'frac':0.3},
        'post_proc': {'info_recon':InfoRecon().unsecure,'priv_amp':PrivAmp().univ2},
        'priv_params':{'final_key_length':32, 'family_size':256},
        'num_signal': 1000,
        'num_simulations':12,
        'debug':True
    }
    plot_rate_vs(param,'darkcount',np.linspace(0.1,10,10),None,'darkcount')

    


# s = Simulation(protocol=DPS(),
    #     qchannel= Fiber(0.3),
    #     signal_params={'alpha':1},
    #     detect_params={},
    #     num_detectors=2,
    #     darkcount_rate=1e1,
    #     clk=1,
    #     delay=channel_data['delay'],
    #     num_signal=100)

    # s = Simulation(protocol=COW(),
    #     qchannel= Fiber(0.3),
    #     signal_params={'alpha':1,'decoy_rate':0.2},
    #     detect_params={'transmitivity':0.9},
    #     num_detectors=3,
    #     darkcount_rate=1e1,
    #     clk=1,
    #     delay=channel_data['delay'],
    #     num_signal=100)