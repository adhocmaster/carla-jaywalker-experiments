

from agents.vehicles.qnactr.servers.BaseCognitiveServer import *
from agents.vehicles.qnactr.Request import Request



class LongTermMemory(BaseCognitiveServer):

    def __init__(self, queue_length=10, frequency=2, subtasks_parameters=None):
        super().__init__(queue_length, frequency)
        self.tick_counter = 0
        if subtasks_parameters is None:
            self.subtasks_parameters = {
                'subtasks_parameters': {
                    'lane_following': {
                        'desired_velocity': 3.5 , # m/s
                        'safe_time_headway': 1.5, # s
                        'max_acceleration': 0.73, # m/s^2
                        'comfort_deceleration': 1.67, # m/s^2
                        'acceleration_exponent': 4, 
                        'minimum_distance': 2, # m
                        'vehicle_length': 1, # m
                    },
                    'lane_keeping': {
                        'far_distance': 15.0,
                    }, 
                },
            }
        self.subtask_parameters = subtasks_parameters
        pass

    def add_request(self, request):
        super().add_request(request)
        # print(f'LongTermMemory add_request {request}')
        pass

    def process_request(self):

        self.tick_counter += 1
        if self.tick_counter % self.frequency == 0:
            if len(self.request_queue) == 0:
                return
            curRequest = self.request_queue.pop(0)
            if curRequest.data.__contains__('far_distance'):
                response_dict = {'far_distance': self.get_far_distance()}
                curRequest.after_process(response_dict)
                self.response_queue.append(curRequest)

            if curRequest.data.__contains__('idm_parameters'):
                # print('processing IDM request ...')
                response_dict = {'idm_parameters': self.get_idm_parameters()}
                curRequest.after_process(response_dict)
                self.response_queue.append(curRequest)
            pass
        pass


    def get_response(self):
        # print(f'get response {self.response_queue}')
        return super().get_response()


    def get_far_distance(self):
        return self.subtask_parameters['lane_keeping']['far_distance'] 

    def get_idm_parameters(self):
        return self.subtask_parameters['lane_following']


    # def __init__(self, frequency=1):
    #     super().__init__(frequency)
    #     pass

    # def add_request(self, request):
    #     self._request.append(request)
    #     pass

    # def process_request(self):
    #     if len(self._request) == 0:
    #         return None
    #     else:
    #         curRequest = self._request.pop(0)
    #         if curRequest == 'IDM_parameters':
    #             self.get_IDM_parameters()
    #             pass

    # def get_response(self):
    #     retrieval_buffer = self._response
    #     self.clear_response()
    #     return retrieval_buffer

    # def get_IDM_parameters(self):
    #     result_dict = {'desired_velocity': 30.0 , # km/h
    #                    'safe_time_headway': 0.00041667, # h
    #                    'max_acceleration': 9460.8, # km/h^2
    #                    'comfort_deceleration': 21643.2, # km/h^2
    #                    'acceleration_exponent': 4, 
    #                    'minimum_distance': 0.002, # km
    #                    'vehicle_length': 0.0055, # km
    #                    }
    #     self._response['idm_parameters'] = result_dict


