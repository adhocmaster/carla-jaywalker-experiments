

from agents.vehicles.qnactr.servers.BaseCognitiveServer import BaseCognitiveServer
# from .._enum import RequestType

class MotorControl(BaseCognitiveServer):
    def __init__(self, queue_length=10, frequency=2):
        super().__init__(queue_length, frequency)

        self.tick_counter = 0
        self.target_velocity = -1.0
        self.target_waypoint = None

        pass

    def add_request(self, request):
        super().add_request(request)
        pass

    # Request data structure does not have distinction between
    # request types. motor control server can receive two types of request 
    # 1. motor control request = changes the value of target velocity and target waypoint
    # 2. memory access request = returns the value of target velocity and target waypoint
    # if the target_velocity and target_waypoint are not set yet, the memory access 
    # request is ignored
    # if the request have target_velocity = -1 or target_waypoint = None
    # the request is considered as a memory access request
    # if the request have target_velocity > 0 or target_waypoint is not none 
    # the request is considered as a motor control request

    def process_request(self):

        self.tick_counter += 1
        if self.tick_counter % self.frequency == 0:
            if len(self.request_queue) == 0:
                return
            curRequest = self.request_queue.pop(0)
            
            if curRequest.data.__contains__('target_velocity'):
                self.process_target_velocity(curRequest)
            if curRequest.data.__contains__('target_waypoint'):
                self.process_target_waypoint(curRequest)        
            pass
        

    

    def process_target_velocity(self, curRequest):
        # if the request have 'target_velocity' key 
        # check if the value for the 'target_velocity' key is -1
            # if yes: the request is considered as a memory access request
                # if the current self._target_velocity is -1, the request is ignored
                # else the request is processed (send back to the sender) with
                # current self._target_velocity 
            # if no: the request is considered as a motor control request
            # update the current self._target_velocity 
        target_velocity = curRequest.data['target_velocity']
        if target_velocity == -1:
            if self.target_velocity == -1:
                return
            else:
                response_dict = {'target_velocity': self.target_velocity}
                curRequest.after_process(response_dict)
                self.response_queue.append(curRequest)
        else: 
            self.target_velocity = target_velocity
            # print(f'updated the target velocity to {self.target_velocity}')
        pass

    def process_target_waypoint(self, curRequest):
        target_waypoint = curRequest.data['target_waypoint']
        if target_waypoint is None:
            if self.target_waypoint is None:
                return
            else:
                response_dict = {'target_waypoint': self.target_waypoint}
                curRequest.after_process(response_dict)
                self.response_queue.append(curRequest)
        else: 
            self.target_waypoint = target_waypoint
            # print(f'updated the target waypoint to {self.target_waypoint}')

    def get_response(self):
        return super().get_response()







