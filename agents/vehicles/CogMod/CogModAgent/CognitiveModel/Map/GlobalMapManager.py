
from agents.navigation.global_route_planner import GlobalRoutePlanner

class GlobalMapManager(GlobalRoutePlanner):

    def __init__(self, wmap, start_transform, destination_transform, sampling_resolution=1.0):
        super().__init__(wmap, sampling_resolution)
        self.start_transform = start_transform
        self.destination_transform = destination_transform

        self.global_plan = self.set_global_plan(self.start_transform, self.destination_transform)
        self.road_list = self.create_road_list_from_global_plan()
        pass

    def create_road_list_from_global_plan(self):
        road_dict = {}
        road_list = []
        for wp, _ in self.global_plan:
            # print(f'road id: {wp.road_id}, s: {wp.s}')
            if wp.road_id not in road_dict.keys():
                road_dict[wp.road_id] = True
                road_list.append(wp.road_id)
                pass
        return road_list
    
    def get_global_plan(self):
        if self.global_plan is None:
            raise ValueError('need to have global plan')
            return None
        return self.global_plan

    def set_global_plan(self, start_transform, end_transform):

        if not start_transform or not end_transform:
            raise ValueError('need to have start and end for global plan')
        print(f'start transform: {start_transform}, \nend transform: {end_transform}')
        self.global_plan = self.trace_route(start_transform.location, end_transform.location)
        return self.global_plan
        

    def update_global_plan(self, location):

        tuple_to_discard = []
        nearest_waypoint = self._wmap.get_waypoint(location)
        # sometimes due to high speed vehcile misses some waypoint at the end of the roads
        # next block ensures all the waypoints are removed properly
        self.remove_residual_waypoints(tuple_to_discard, nearest_waypoint)
        self.remove_waypoint_on_same_road(tuple_to_discard, nearest_waypoint)
        self.discard_tuple_from_global_plan(tuple_to_discard)


    def discard_tuple_from_global_plan(self, tuple_to_discard):
        if len(tuple_to_discard) != 0:
            for ttd in tuple_to_discard:
                self.global_plan.remove(ttd)
                pass

    def remove_waypoint_on_same_road(self, tuple_to_discard, nearest_waypoint):
        for wp, ro in self.global_plan:
            # print(f'wp road id : {wp.road_id}, s {wp.s}, nearest {nearest_waypoint.road_id}, s {nearest_waypoint.s}')
            if wp.road_id == nearest_waypoint.road_id:
                # need this for the road direction formation according to 
                # OpenDRIVE's road direction
                if wp.lane_id < 0:
                    if wp.s <= nearest_waypoint.s:
                        tuple_to_discard.append((wp, ro))
                elif wp.lane_id > 0:
                    if wp.s >= nearest_waypoint.s:
                        tuple_to_discard.append((wp, ro))

    # really big function 
    def remove_residual_waypoints(self, tuple_to_discard, nearest_waypoint):
        for i in self.road_list:
            if nearest_waypoint.road_id == i:
                while nearest_waypoint.road_id != self.road_list[0]:
                    for wp, ro in self.global_plan:
                        if wp.road_id == self.road_list[0]:
                            tuple_to_discard.append((wp, ro))
                    
                    # self.cur_road_id = nearest_waypoint.road_id
                    self.road_list.pop(0)
                break
                