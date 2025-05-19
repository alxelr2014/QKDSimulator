from qkd_protocol import *
from bb84 import *
from cow import *
from dps import *
import numpy as np
import matplotlib.pyplot as plt
import heapq

class Event:
    def __init__(self, time, action, description=''):
        self.time = time
        self.action = action  
        self.description = description

    def __lt__(self, other):
        return self.time < other.time  

class Simulation:
    def __init__(self,protocol : QKDProtocol, qchannel : QuantumChannel, signal_params,detect_params, num_detectors, darkcount_rate,clk, delay,
                 num_signal = 100):
        self.protocol = protocol
        self.qchannel = qchannel
        self.signal_params = signal_params
        self.detect_params = detect_params
        self.num_detectors = num_detectors
        self.darkcount_rate = darkcount_rate
        self.clk = clk
        self.delay = delay
        self.num_signal = num_signal
        self.sent_signal = 0
        self.alice_data = []
        self.bob_data = []
        self.current_time = 0
        self.event_queue = []  

    def schedule_event(self, event):
        heapq.heappush(self.event_queue, event)

    def run_qkd(self):
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time
            print(f"Time {self.current_time}: Executing {event.description}")
            event.action(self.current_time)
        return self.alice_data, self.bob_data

    def start_event(self,time):
        self.schedule_event(Event(0,self.generate_signal,'Generate Signal'))
        for _ in range(self.num_detectors):
            self.schedule_event(Event(np.random.exponential(self.darkcount_rate),self.darkcount(_),'Dark Count'))
    
    def generate_signal(self, time):
        if self.sent_signal < self.num_signal:
            self.alice_data.append(self.protocol.signal_generation(self.signal_params | {'time' : time}))
            self.schedule_event(Event(time,self.transmit(self.alice_data[-1]['signal']),'Transmit'))
            self.schedule_event(Event(time + self.clk, self.generate_signal,'Generate Signal'))
            self.sent_signal += 1
        else:
            self.schedule_event(Event(time + 10*self.clk,self.terminate,'Terminate'))

    def transmit(self,signal):
        def transmit_signal(time):
            received = self.qchannel.transmit(signal)
            self.schedule_event(Event(time + self.delay, self.detect(received),'Detect Signal'))
        return transmit_signal

    def detect(self,received):
        def detect_signal(time):
            self.bob_data.append(self.protocol.detection({'received':received, 'dark_count' : np.zeros(self.num_detectors), 'time' : time} 
                                                         | self.detect_params))
        return detect_signal

    def darkcount(self,ind):
        def dc(time):
            v = np.zeros(self.num_detectors)
            v[ind] = 1
            self.bob_data.append(self.protocol.detection({'dark_count':v, 'time': time}))
            self.schedule_event(Event(time + np.random.exponential(self.darkcount_rate),self.darkcount(ind),'Dark Count'))
        return dc

    def terminate(self,time):
        self.event_queue.clear()
    
    def sifting(self,alice_data,bob_data, channel_data):
        aparams,bparams =  self.protocol.sift_darkcount(alice_data,bob_data,channel_data)
        return self.protocol.sift(aparams,bparams)
    
    def param_est(self,params):
        return self.protocol.param_est(params)


def print_result(pe):
    print('Alice\'s Key: ', pe['akey'])
    print('Bob\'s Key:   ', pe['bkey'])
    print('QBER: ', pe['qber'])
    print('Rate: ', np.size(pe['akey'])/pe['num_signal'])
    print('Number of errors: ', np.sum(np.logical_xor(pe['akey'],pe['bkey'])))

if __name__ == "__main__":
    channel_data = {'delay' : 1e-2, 'margin' : 1e-3}
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

    s = Simulation(protocol=BB84(),
        qchannel= Fiber(10),
        signal_params={'alpha':3,'mu' : 0.1, 'decoy_rate':0.2},
        detect_params={},
        num_detectors=1,
        darkcount_rate=5.2,
        clk=1,
        delay=1e-2,
        num_signal=1000)
    s.schedule_event(Event(0,s.start_event,'Start'))
    alice_data, bob_data = s.run_qkd()
    keys = s.sifting(alice_data,bob_data,channel_data)
    pe = s.param_est(keys | {'frac':0.3})
    print_result(pe | {'num_signal' : 1000})
