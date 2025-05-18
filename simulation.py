from qkd_protocol import *
from bb84 import *
from cow import *
from dps import *
import numpy as np
import matplotlib.pyplot as plt
# import heapq

# # Event class
# class Event:
#     def __init__(self, time, action, description=''):
#         self.time = time
#         self.action = action  # Callable function
#         self.description = description

#     def __lt__(self, other):
#         return self.time < other.time  # for priority queue

# # Simulation engine
# class Simulation:
#     def __init__(self):
#         self.current_time = 0
#         self.event_queue = []  # Priority queue

#     def schedule_event(self, event):
#         heapq.heappush(self.event_queue, event)

#     def run(self, until=float('inf')):
#         while self.event_queue and self.current_time <= until:
#             event = heapq.heappop(self.event_queue)
#             self.current_time = event.time
#             print(f"Time {self.current_time}: Executing {event.description}")
#             event.action(self)

# # Example actions
# def example_event(sim):
#     print(" -> Example event executed")
#     # You can schedule new events here:
#     # sim.schedule_event(Event(time=sim.current_time + 5, action=example_event, description="Next example event"))

# # Usage
# if __name__ == "__main__":
#     sim = Simulation()
#     sim.schedule_event(Event(time=10, action=example_event, description="First example event"))
#     sim.schedule_event(Event(time=5, action=example_event, description="Second example event"))
#     sim.run(until=20)


class Simulation:
    def __init__(self,protocol : QKDProtocol, qchannel : QuantumChannel, signal_params,detect_params,est_params,
                 num_signal = 100):
        self.protocol = protocol
        self.qchannel = qchannel
        self.signal_params = signal_params
        self.detect_params = detect_params
        self.num_signal = {'num_signal':num_signal}
        self.est_params = est_params
    
    def run(self):
        states = self.protocol.signal_generation(self.signal_params | self.num_signal)

        seq_trans = np.vectorize(self.qchannel.transmit)
        received = seq_trans(states['signals'])

        dectection = self.protocol.detection({'received':received} | self.detect_params | self.num_signal)

        sifted = self.protocol.sift(states | self.num_signal ,dectection)
        pe = self.protocol.param_est(sifted | self.est_params)
        return pe|self.num_signal
    
def print_result(pe):
    print('Alice\'s Key: ', pe['akey'])
    print('Bob\'s Key:   ', pe['bkey'])
    print('QBER: ', pe['qber'])
    print('Rate: ', np.size(pe['akey'])/pe['num_signal'])

s = Simulation(BB84(),
        Fiber({}),
        signal_params={'alpha':2,'mu' : 0.1, 'decoy_rate':0.2},
        detect_params={},
        est_params={'frac':0.3},
        num_signal=100)
print_result(s.run())


# s = Simulation(DPS(),
#         Fiber({}),
#         signal_params={'alpha':1},
#         detect_params={},
#         est_params={'frac':0.3},
#         num_signal=100)
# print(s.run())

# s = Simulation(COW(),
#         Fiber({}),
#         signal_params={'alpha':1,'decoy_rate':0.2},
#         detect_params={'transmitivity':0.9},
#         est_params={'frac':0.3},
#         num_signal=100)
# print(s.run())