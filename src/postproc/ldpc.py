from .ldpc_lib import error_correction_lib as ec
from .ldpc_lib.file_utils import codes_from_file
import numpy as np
from os import path
from .inforecon import InfoRecon

class LDPC(InfoRecon):
    def __init__(self,n):
        self.n = n
        dirname = path.dirname(__file__)
        self.codes = codes_from_file(path.join(dirname, 'ldpc_lib\\codes_'+str(n)+'.txt'))
        self.R_range = []
        for code in self.codes:
            self.R_range.append(code[0])
        

    def run(self,params):
        f_start = params['fstart']  # initial efficiency of decoding
        qber = params['qber']
        if qber < 1e-2:
            qber = 0.05
    
        print('\nqber = ', qber)
        n_tries = params['num_tries']
        show = params['show']
        discl_k = params['discl_k']
        R, s_n, p_n = ec.choose_sp(qber, f_start, self.R_range, self.n)
        k_n = self.n-s_n-p_n
        m = (1-R)*self.n
        code_params = self.codes[(R, self.n)]
        s_y_joins = code_params['s_y_joins']
        y_s_joins = code_params['y_s_joins']
        punct_list = code_params['punct_list']
        syndrome_len = code_params['syndrome_len']
        p_n_max = len(punct_list)
        discl_n = int(round(self.n*(0.0280-0.02*R)*discl_k))
        qber_est = qber
        f_rslt = []
        com_iters_rslt = []
        n_incor = 0

        # print("QBER = ", qber, "R =", R, "s_n =", s_n, "p_n =",
        #     p_n, '(', p_n_max, ')', 'discl_n', discl_n)
        olen = np.size(params['akey'])
        blen = self.n-s_n-p_n
        nlen = blen*(olen//blen + 1)
        xs =  np.split(np.pad(params['akey'],(0,nlen-olen),'constant',constant_values=(0,0)),nlen//blen)
        ys =  np.split(np.pad(params['bkey'],(0,nlen-olen),'constant',constant_values=(0,0)),nlen//blen)
        es = np.empty(nlen//blen,dtype=np.ndarray)
        for lind in range(nlen//blen):
            for i in range(n_tries):
                add_info, com_iters, es[lind], ver_check = ec.perform_ec(
                    xs[lind], ys[lind], s_y_joins, y_s_joins, qber_est, s_n, p_n, punct_list=punct_list, discl_n=discl_n, show=show)
                f_cur = float(m-p_n+add_info)/(self.n-p_n-s_n)/(ec.h_b(qber))
                f_rslt.append(f_cur)
                com_iters_rslt.append(com_iters)
                if not ver_check:
                    n_incor += 1
            if show > 0:
                print('Mean efficiency:', np.mean(f_rslt),
                '\nMean additional communication rounds', np.mean(com_iters_rslt),"Effective R: ", (R-(s_n/self.n))/(1-s_n/self.n-p_n/self.n)   )
        x = np.concatenate(xs)[:olen]
        y = np.concatenate(ys)[:olen]
        e = np.concatenate(es)[:olen]
        return {'akey': x, 'bkey': np.logical_xor(y,e)}



