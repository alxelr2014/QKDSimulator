import numpy as np
from heapq import heappop,heappush

from .event import Event
from ..qkd.qkd_protocol import QKDProtocol
from ..qdevices.quantum_channel import QuantumChannel


class Simulation:
    def __init__(self,protocol : QKDProtocol, qchannel : QuantumChannel, signal_params :dict,detect_params :dict, num_detectors:int,
                 darkcount_rate:float,clk:float, delay:float, post_proc:dict, num_signal = 100, debug = False):
        self.protocol = protocol
        self.qchannel = qchannel
        self.signal_params = signal_params
        self.detect_params = detect_params
        self.num_detectors = num_detectors
        self.darkcount_rate = darkcount_rate
        self.clk = clk
        self.delay = delay
        self.post_proc = post_proc
        self.num_signal = num_signal
        self.sent_signal = 0
        self.alice_data = []
        self.bob_data = []
        self.current_time = 0
        self.event_queue = []
        self.debug = debug

    def schedule_event(self, event : Event):
        heappush(self.event_queue, event)

    def run_qkd(self):
        while self.event_queue:
            event = heappop(self.event_queue)
            self.current_time = event.time
            if self.debug:
                print(f"Time {self.current_time}: Executing {event.description}")
            event.action(self.current_time)
        return self.alice_data, self.bob_data

    def start_event(self,time : float):
        self.schedule_event(Event(0,self.generate_signal,'Generate Signal'))
        for _ in range(self.num_detectors):
            self.schedule_event(Event(np.random.exponential(self.darkcount_rate),self.darkcount(_),'Dark Count'))
    
    def generate_signal(self, time : float):
        if self.sent_signal < self.num_signal:
            self.alice_data.append(self.protocol.signal_generation(self.signal_params | {'time' : time}))
            self.schedule_event(Event(time,self.transmit(self.alice_data[-1]['signal']),'Transmit'))
            self.schedule_event(Event(time + self.clk, self.generate_signal,'Generate Signal'))
            self.sent_signal += 1
        else:
            self.schedule_event(Event(time + 10*self.clk,self.terminate,'Terminate'))

    def transmit(self,signal):
        def transmit_signal(time : float):
            received = self.qchannel.transmit(signal)
            self.schedule_event(Event(time + self.delay, self.detect(received),'Detect Signal'))
        return transmit_signal

    def detect(self,received):
        def detect_signal(time: float):
            self.bob_data.append(self.protocol.detection({'received':received, 'dark_count' : np.zeros(self.num_detectors), 'time' : time} 
                                                         | self.detect_params))
        return detect_signal

    def darkcount(self,ind :int):
        def dc(time:float):
            v = np.zeros(self.num_detectors)
            v[ind] = 1
            self.bob_data.append(self.protocol.detection({'dark_count':v, 'time': time}))
            self.schedule_event(Event(time + np.random.exponential(self.darkcount_rate),self.darkcount(ind),'Dark Count'))
        return dc

    def terminate(self,time: float):
        self.event_queue.clear()
    
    def sifting(self,alice_data,bob_data, channel_data):
        aparams,bparams =  self.protocol.sift_darkcount(alice_data,bob_data,channel_data)
        return self.protocol.sift(aparams,bparams)
    
    def param_est(self,params):
        return self.protocol.param_est(params)
    
    def info_recon(self,params):
        return self.post_proc['info_recon'](params)
    
    def priv_amp(self,params):
        return self.post_proc['priv_amp'](params)
