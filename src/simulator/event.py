
class Event:
    def __init__(self, time : float, action, description=''):
        self.time = time
        self.action = action  
        self.description = description

    def __lt__(self, other:float):
        return self.time < other.time