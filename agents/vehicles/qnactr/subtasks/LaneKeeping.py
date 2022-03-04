

from enum import Enum

from agents.vehicles.qnactr.Request import Request
from ..qnactr_enum import ServerType, SubtaskState, SubtaskType



# Lane keeping subtask is used to keep the vehicle on the lane.
# subtasks are created by the agent and keep a reference of the 
# localmap and vehicle location.
# onTick works on every tick and accumulate response
# lateTick triggered after the tick_frequency is reached
# lateTick check if the required values are available and 
#   if not, it will create request for survers for necessary information
#   and go into a Halt state 
#   if yes, it will create a cognitive process request to ComplexCognitionServer

class LaneKeeping():
    def __init__(self, localMap):
        print(f'LaneKeeping.__init__()')
        self.tick_frequency = 1
        self.tick_counter = 0

        self.local_map = localMap

        self.request_queue = []
        self.response_queue = []

        self.local_memory = {'far_distance': -1, 'next_waypoint': None}
        self.subtask_state = SubtaskState.ACTIVE
        pass


    def get_request(self):
        result = self.request_queue
        self.request_queue = []
        return result
    
    # on every tick increase counter and accumulate responses 
    def onTick(self, localMap, responses):
        self.tick_counter += 1
        self.local_map = localMap
        for response in responses:
            self.response_queue.append(response)
            pass
        # print(f'accumulating responses')
        if self.tick_counter % self.tick_frequency == 0:
            self.lateTick(self.response_queue)
            self.response_queue = []
            pass

        pass

    # late tick is triggered when the tick_frequency is reached
    # deals with two responses:
    #   1. far_distance memory access response from LongTermMemoryServer
    #   2. computation response from ComplexCognitionServer
    # after completing the lateTick sets the far_distance to -1 


    # psudocode:
    # process the responses from the servers
    #   for each response in the queue:
    #       if response data has far_distance:
    #           set far_distance to response data
    #       if response data has next_waypoint:
    #           set next_waypoint to response data


    #  process if the next_waypoint is available 
    #  if next_waypoint is not None:
    #      create a request to MotorControl server with the next_waypoint
    #      add the request to the request_queue
    #      set the local_memory to -1 and None
    #      set state to ACTIVE
    #      break
    #   elif far_distance is -1 and state is ACTIVE:
    #       create request for LongTermMemoryServer for far_distance
    #       set state to HALT
    #   elif far_distance is not -1 and state is HALT:
    #       create request for ComplexCognitionServer for next_waypoint
    #       set state to HALT

    def lateTick(self, responses_queue):
        # print(f'LaneKeeping.lateTick()')
        for response in responses_queue:
            if response.data.__contains__('far_distance'):
                # print('far distance data arrived')
                self.local_memory['far_distance'] = response.data['far_distance']
                pass
            if response.data.__contains__('next_waypoint'):
                # print('next waypoint data arrived')
                self.local_memory['next_waypoint'] = response.data['next_waypoint']
                pass
            pass

        if self.local_memory['next_waypoint'] is not None \
                and self.subtask_state is SubtaskState.HALT:
            # print(f'all data available')
            request = Request(SubtaskType.LANEKEEPING, ServerType.MOTOR_CONTROL, {'target_waypoint': self.local_memory['next_waypoint']})
            self.request_queue.append(request)
            self.local_memory['far_distance'] = -1
            self.local_memory['next_waypoint'] = None
            self.subtask_state = SubtaskState.ACTIVE
            pass
        elif self.local_memory['far_distance'] == -1 \
            and self.subtask_state == SubtaskState.ACTIVE:
            # print(f'far distance is -1 and state is ACTIVE')
            request = Request(SubtaskType.LANEKEEPING, ServerType.LONGTERM_MEMORY, {'far_distance': -1})
            self.request_queue.append(request)
            self.subtask_state = SubtaskState.HALT
            pass
        elif self.local_memory['far_distance'] != -1 \
            and self.subtask_state == SubtaskState.HALT:
            # print(f'far distance is not -1 and state is HALT')
            request = Request(SubtaskType.LANEKEEPING, 
                              ServerType.COMPLEX_COGNITION, 
                              {'far_distance': self.local_memory['far_distance'], 'local_map': self.local_map})
            self.request_queue.append(request)
            # self.subtask_state = SubtaskState.HALT
            self.local_memory['far_distance'] = -1
            pass
        pass



  