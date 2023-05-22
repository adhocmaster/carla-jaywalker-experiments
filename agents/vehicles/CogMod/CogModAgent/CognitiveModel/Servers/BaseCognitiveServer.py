from abc import ABC, abstractmethod
from enum import Enum

from agents.vehicles.CogMod.CogModEnum import SubtaskType

class BaseCognitiveServer(ABC):
    def __init__(self, queue_length=10, frequency=5):
        super().__init__()
        self.queue_length = queue_length
        self.frequency = frequency
        self.request_queue = []
        self.response_queue = []
        pass

    #  if the queue is full, the oldest request is removed
    @abstractmethod
    def add_request(self, request):
        if len(self.request_queue) > self.queue_length:
            self.request_queue.pop(0)
        self.request_queue.append(request)
        pass
    
    # the expectation is that the server will process the request 
    #  and store the response in the response queue
    @abstractmethod
    def process_request(self):
        pass

    @abstractmethod
    def get_response(self):
        result = self.response_queue
        self.reset_response_queue()
        return result

    def reset_request_queue(self):
        self.request_queue = []
        pass

    def reset_response_queue(self):
        self.response_queue = []
        pass


    def print_server_stats(self):
        lane_keeping_request_count = 0
        lane_following_request_count = 0
        for request in self.request_queue:
            if request.sender == SubtaskType.LANEFOLLOWING:
                lane_following_request_count += 1
            if request.sender == SubtaskType.LANEKEEPING:
                lane_keeping_request_count += 1
        print(f'request_count: LF {lane_following_request_count}, LK: {lane_keeping_request_count}')
        print(f'request_count: {len(self.request_queue)}, response_count: {len(self.response_queue)}')
        pass