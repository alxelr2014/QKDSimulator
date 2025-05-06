import heapq

# Event class
class Event:
    def __init__(self, time, action, description=''):
        self.time = time
        self.action = action  # Callable function
        self.description = description

    def __lt__(self, other):
        return self.time < other.time  # for priority queue

# Simulation engine
class Simulation:
    def __init__(self):
        self.current_time = 0
        self.event_queue = []  # Priority queue

    def schedule_event(self, event):
        heapq.heappush(self.event_queue, event)

    def run(self, until=float('inf')):
        while self.event_queue and self.current_time <= until:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time
            print(f"Time {self.current_time}: Executing {event.description}")
            event.action(self)

# Example actions
def example_event(sim):
    print(" -> Example event executed")
    # You can schedule new events here:
    # sim.schedule_event(Event(time=sim.current_time + 5, action=example_event, description="Next example event"))

# Usage
if __name__ == "__main__":
    sim = Simulation()
    sim.schedule_event(Event(time=10, action=example_event, description="First example event"))
    sim.schedule_event(Event(time=5, action=example_event, description="Second example event"))
    sim.run(until=20)
