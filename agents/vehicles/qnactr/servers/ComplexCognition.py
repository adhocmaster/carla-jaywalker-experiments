
import carla
from agents.vehicles.qnactr.servers.BaseCognitiveServer import BaseCognitiveServer
from agents.vehicles.qnactr.subtasks.IDM import IDM


class ComplexCognition(BaseCognitiveServer):
    def __init__(self, queue_length=10, frequency=5):
        super().__init__(queue_length, frequency)
        self.tick_counter = 0
        pass

    def add_request(self, request):
        super().add_request(request)
        pass

    # complex cognition server doews the following:
    # 1. Lane keeping subtask send request to calculate the next
    # waypoint with far_distance and the current vehicle location and local map
    # lane keeping sends request with the far_distance value, 
    # current vehicle location and local map in a dictionary

    def process_request(self):

        self.print_request_queue_stats()
        self.tick_counter += 1
        if self.tick_counter % self.frequency == 0:

            if len(self.request_queue) == 0:
                return
            
            curRequest = self.request_queue.pop(0)
            if curRequest.data.__contains__('far_distance') and curRequest.data.__contains__('local_map'):
                response_dict = {'next_waypoint': self.get_next_waypoint(curRequest)}
                curRequest.after_process(response_dict)
                self.response_queue.append(curRequest)

            if curRequest.data.__contains__('idm_parameters') and curRequest.data.__contains__('local_map'):
                response_dict = {'next_velocity': self.get_next_velocity(curRequest)}
                curRequest.after_process(response_dict)
                self.response_queue.append(curRequest)

            pass
        pass

    def get_response(self):
        return super().get_response()


    def get_next_velocity(self, curRequest):

        localMap = curRequest.data['local_map']
        idm_parameters = curRequest.data['idm_parameters']

        idm = IDM(idm_parameters, localMap)
        velocity = idm.calc_velocity() * 3.6

        # print(f'next velocity is {velocity}')

        return velocity

    def get_next_waypoint(self, curRequest):
        #   process one step for the subtasks 
        #   for Lane keeping subtask, check current nearest waypoint 
        #   and find a waypoint that is far_distance ahead of the vehicle's nearest
        #   waypoint. 
        localMap = curRequest.data['local_map']
        farDistance = curRequest.data['far_distance']

        # print(f'far distance is {farDistance}, local map is {localMap}')

        #   get the nearest waypoint to the vehicle 
        vehicle_location = localMap.vehicle.get_location()
        # print(f'vehicle location is {vehicle_location}')
        nearest_waypoint = localMap.map.get_waypoint(vehicle_location)

        # iterate over the waypoints from global plan and print distance 
        next_waypoint = None  #  waypoint immediately after far distance
        distance = 0 
        for wp, _ in localMap.global_plan:
            distance += wp.transform.location.distance(nearest_waypoint.transform.location)
            if distance > farDistance:
                # print(f'waypoint is {wp}')
                next_waypoint = wp
                break
        if next_waypoint is None and len(localMap.global_plan) > 0:
            # print('not enough waypoints in the global plan so sending the last waypoint')
            next_waypoint = localMap.global_plan[-1][0]

        return next_waypoint

        
        

    

 