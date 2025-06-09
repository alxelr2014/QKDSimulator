import numpy as np
import matplotlib.pyplot as plt
from functools import partial
from multiprocessing import Pool
from Crypto.Random import get_random_bytes
from Crypto.Hash import HMAC, SHA256
from tqdm import tqdm


from src.qkd import DPS,BB84,COW
from src.postproc.inforecon import InfoRecon
from src.postproc.privamp import PrivAmp
from src.qdevices import Fiber
from src.simulator import Simulation,Event

hex_hash_key = get_random_bytes(16)
def secure_hash_using_hmac( data):
    h = HMAC.new(hex_hash_key, digestmod=SHA256)
    h.update(data)
    return h.hexdigest()

def bytify(bitvec):
    return secure_hash_using_hmac(bytes(np.packbits(bitvec)))

def print_result(pe,n,str):
    print("############## "+str+" ##############")
    print('Alice\'s Key: ', (pe['akey']))
    print('Bob\'s Key:   ', (pe['bkey']))
    if 'qber' in pe:
        print('QBER: ', pe['qber'])
    print('Rate: ', np.size(pe['akey'])/n)
    print('Number of errors: ', np.sum(np.logical_xor(pe['akey'],pe['bkey'])))
    print("############################")


def dic_update(dic,key,val):
    for k in dic.keys():
        if key == k:
            dic[k] = val
        if isinstance(dic[k], dict):
            dic[k] = dic_update(dic[k],key,val)
    return dic


def get_result(pe,ir,pa,num_signal,res_labels):
    results = np.empty(np.size(res_labels))
    for i in range(np.size(res_labels)):
        if res_labels[i] == 'Param Est Rate':
            results[i] = np.size(pe['akey'])/num_signal
        elif res_labels[i] == 'Priv Amp Rate':
            results[i] = np.size(pa['akey'])/num_signal
        elif res_labels[i] == 'QBER':
            results[i] = pe['qber'] + 1e-8
        elif res_labels[i] == 'Param Est Error':
            results[i] = np.sum(np.logical_xor(pe['akey'],pe['bkey']))/np.size(pe['akey'])+1e-8
        elif res_labels[i] == 'Priv Amp Error':
            results[i] = np.sum(np.logical_xor(pa['akey'],pa['bkey']))/np.size(pa['akey'])+1e-8
    
        else:
            results[i] = -1
    return results





def simulate_vs(v,param,label,res_labels):
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

    ir = s.info_recon(pe)

    pa = s.priv_amp(ir | param['priv_params'])

    # print_result(pe , param['num_signal'], 'Parameter Estimation')
    # print_result(ir , param['num_signal'], 'Information Reconcilliation' )
    # priv_rate = print_result(pa , param['num_signal'], 'Privacy Amplification')
    return get_result(pe,ir,pa,param['num_signal'],res_labels)


def get_data(params,var_labels,var_range,num_proc,res_labels):
    results = np.empty(params['num_simulations'],dtype=np.ndarray)
    for _ in tqdm(range(params['num_simulations'])):
        with Pool(num_proc) as p:
            results[_] = np.array(p.map(partial(simulate_vs, param=params,label=var_labels, res_labels=res_labels), var_range))
    results= np.average(results,axis=0)
    return results

def plot_rate_vs(params,var_label,var_range,num_proc,res_labels,xlabel, ylabel,title,logarithmic = False, filename = 'test'):
    results = get_data(params,var_label,var_range,num_proc,res_labels)

    fig, ax = plt.subplots()
    ax.plot(var_range, results, label = res_labels)

    ax.set(xlabel=xlabel, ylabel=ylabel, title= title)
    if logarithmic:
        ax.set_yscale('log')
    else:
        ax.set_ylim(0.0,0.6)
    ax.grid()
    ax.legend(loc='upper left')

    fig.savefig('./Figure/'+filename+'.png')
    plt.show()



if __name__ == "__main__":
    param = {
        'protocol' : COW(),
        'qchannel' : Fiber,
        'qchannel_params': {'length' : 2, 'gamma' : 0.2},
        'signal_params' : {'alpha':0.7,'mu' : 0.1, 'decoy_rate':0.5},
        'detect_params' : {'transmitivity': 0.9},
        'num_detectors' : 3,
        'darkcount_rate': 1e-1,
        'clk' : 1,
        'channel_data': {'delay' :  1e-2, 'margin' : 1e-3},
        'est_params': {'frac':0.3},
        'post_proc': {'info_recon':InfoRecon().unsecure,'priv_amp':PrivAmp().univ2},
        'priv_params':{'final_key_length':32, 'family_size':256},
        'num_signal': 10000,
        'num_simulations':100,
        'debug':False
    }
    plot_rate_vs(
        params=param,
        var_label='dakrcount_rate',
        var_range=np.linspace(1e-3,1,20),
        num_proc=None,
        res_labels=['QBER', 'Param Est Error'],
        xlabel='Darkcount (Hz)',
        ylabel='Error Probability',
        title='Darkcount vs Error Probability',
        logarithmic=False,
        filename='Darkcount cow error')

