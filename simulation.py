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

from bb84 import *
from cow import *
from dps import *
import numpy as np
import matplotlib.pyplot as plt

def bb84decoy(num_sim,num_signal):
    alphas = np.linspace(0.1,2.1,10)
    rates = np.empty(np.size(alphas))
    for i in range(np.size(alphas)):
        rates[i] = 0
        for j in range(num_sim):
            s = BB84({'alpha':alphas[i],'mu' : 0.1, 'decoy_rate':0.2, 'qchannel':Fiber({})})
            akey= s.run_protocol(params={'num_signal':num_signal})[0]
            rates[i] += np.size(akey)/num_signal
        rates[i] /= num_sim
    plt.ylabel('Rate')
    plt.xlabel("Intensity (alpha)")
    plt.title('BB84 Decoy')
    plt.plot(alphas,rates)
    plt.show()


def cowqdk(num_sim, num_signal):
    alphas = np.linspace(0.1,2.1,100)
    rates = np.empty(np.size(alphas))
    for i in range(np.size(alphas)):
        rates[i] = 0
        for j in range(num_sim):
            s = COW({'alpha':alphas[i], 'decoy_rate':0.2, 'qchannel':Fiber({}),'transmitivity':0.9})
            akey= s.run_protocol({'num_signal':num_signal})[0]
            rates[i] += np.size(akey)/num_signal
        rates[i] /= num_sim
    plt.ylabel('Rate')
    plt.xlabel("Intensity (alpha)")
    plt.title('COW')
    plt.plot(alphas,rates)
    plt.show()
   
def dpsqkd(num_sim, num_signal):
    alphas = np.linspace(0.1,2.1,10)
    rates = np.empty(np.size(alphas))
    for i in range(np.size(alphas)):
        rates[i] = 0
        for j in range(num_sim):
            s = DPS({'alpha':alphas[i],'qchannel':Fiber({})})
            akey= s.run_protocol(params={'num_signal':num_signal})[0]
            rates[i] += np.size(akey)/num_signal
        rates[i] /= num_sim
    plt.ylabel('Rate')
    plt.xlabel("Intensity (alpha)")
    plt.title('COW')
    plt.plot(alphas,rates)
    plt.show()
    

cowqdk(100,500)