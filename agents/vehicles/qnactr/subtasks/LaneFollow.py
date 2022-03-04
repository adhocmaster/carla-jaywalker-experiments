#  Lane follow task is implemented using the Intelligent Driver Model (IDM)



from agents.vehicles.qnactr.Request import Request
# from agents.vehicles.qnactr.servers.BaseCognitiveServer import ServerType
from ..qnactr_enum import ServerType
# from agents.vehicles.qnactr.subtasks.LaneKeeping import SubtaskState, SubtaskType
from ..qnactr_enum import SubtaskState, SubtaskType

class LaneFollow():
    def __init__(self, localMap):
        print('LaneFollow __init__()')

        self.tick_frequency = 1
        self.tick_counter = 0
        self.IDM = None

        self.request_queue = []
        self.response_queue = []

        self.local_map = localMap

        self.local_memory = { 'idm_parameters' : None, 
                              'next_velocity' : -1
                            }
                                                 

        self.subtask_state = SubtaskState.ACTIVE


    def get_request(self):
        result = self.request_queue
        self.request_queue = []
        return result

    # on every tick increase counter and accumulate responses
    def onTick(self, localMap, responses):
        # print('LaneFollow onTick()')
        self.tick_counter += 1
        self.local_map = localMap
        
        for response in responses: 
            self.response_queue.append(response)
            pass

        if self.tick_counter % self.tick_frequency == 0:
            self.lateTick(self.response_queue)
            self.response_queue = []
            pass

        pass

    # late tick is triggered after the tick frequency is reached 
    # deals with two responses:
    #   1. IDM parameters from the LongTermMemoryServer
    #   2. computation response from the ComplexCognitionServer


    def lateTick(self, responses_queue):
        # print('LaneFollow lateTick()')
        for response in responses_queue:
            # print(f'response: {response}')
            if response.data.__contains__('idm_parameters'):
                self.local_memory['idm_parameters'] = response.data['idm_parameters'] 
                pass
            if response.data.__contains__('next_velocity'):
                self.local_memory['next_velocity'] = response.data['next_velocity']
                pass
        
        if self.local_memory['next_velocity'] is not -1 \
                and self.subtask_state is SubtaskState.HALT:
            # print('everyting in place... sending request to motor control')
            request = Request(SubtaskType.LANEFOLLOWING, ServerType.MOTOR_CONTROL, {'target_velocity': self.local_memory['next_velocity']})
            self.request_queue.append(request)
            self.local_memory['idm_parameters'] = None
            self.local_memory['next_velocity'] = -1
            self.subtask_state = SubtaskState.ACTIVE
            pass

        elif self.local_memory['idm_parameters'] is None \
            and self.subtask_state == SubtaskState.ACTIVE:
            # print('no parameters yet... sending request to long term memory')
            request = Request(SubtaskType.LANEFOLLOWING, ServerType.LONGTERM_MEMORY, {'idm_parameters': None})
            self.request_queue.append(request)
            self.subtask_state = SubtaskState.HALT
            pass
        elif self.local_memory['idm_parameters'] is not None \
            and self.subtask_state == SubtaskState.HALT:
            # print('parameters received... sending request to complex cognition')
            request = Request(SubtaskType.LANEFOLLOWING, 
                              ServerType.COMPLEX_COGNITION, 
                              {'idm_parameters': self.local_memory['idm_parameters'], 'local_map': self.local_map})
            self.request_queue.append(request)
            # self.subtask_state = SubtaskState.HALT
            self.local_memory['idm_parameters'] = None
            pass
        pass



        