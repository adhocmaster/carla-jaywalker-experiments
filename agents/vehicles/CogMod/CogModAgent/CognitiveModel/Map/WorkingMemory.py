
import carla

SCALE_FACTOR = 4 * 0.10106

class WorkingMemory():

    def __init__(self):

        self.tracked_vehicle_id = None

        self.location_t_1 = carla.Vector3D()
        self.location_t_2 = carla.Vector3D()
        self.velocity_t_1 = carla.Vector3D()

        self.ego_location_t_1 = carla.Vector3D()
        # self.ego_location_t_2 = carla.Vector3D()

        self.previous_ego_velocity = None
        pass
    
    # types of parameters:
    # ego_velocity: carla.Vector3D
    # other_vehicle: carla.Vehicle
    # del_t: float
    # we work with only location data 
    # we approximate velocity from the ego location data
    def update(self, ego_vehicle, other_vehicle, del_t):
        
        location_t = None
        preceding_vehicle_velocity = None
        # we have not created the working memory yet when previous_ego_velocity is None
        if self.previous_ego_velocity is None:
            self.previous_ego_velocity = ego_vehicle.get_velocity()
            pass
        # we have a tracked vehicle where driver is looking at 
        # so actual update
        if other_vehicle is not None:
            # print('actual update')
            self.tracked_vehicle_id = other_vehicle.id
            location_t = other_vehicle.get_location()
        else:
            # other vehicle is none; can happen for one resons:
            # 1. we are updating the working memory with dead reconing 
            # print('approximate update')
            # chekcing if we were tracking a vehicle before
            if self.tracked_vehicle_id is None:
                #  we are not tracking a vehicle before and no vehicle came as other vehicle
                location_t = ego_vehicle.get_location() + 100 * ego_vehicle.get_velocity().make_unit_vector()
                self.location_t_1 = ego_vehicle.get_location() + 99 * ego_vehicle.get_velocity().make_unit_vector()
                pass
            else:
                preceding_vehicle_velocity = (self.location_t_1 - self.location_t_2) / del_t
                diff_velocity = preceding_vehicle_velocity - self.previous_ego_velocity
                location_t = self.location_t_1 + diff_velocity * del_t

        
        self.location_t_2 = self.location_t_1
        self.location_t_1 = location_t 
        self.previous_ego_velocity = ego_vehicle.get_velocity()
        self.ego_location_t_1 = ego_vehicle.get_location()

        if preceding_vehicle_velocity is None:
            self.velocity_t_1 = (self.location_t_1 - self.location_t_2) / del_t
            pass
        else:
            self.velocity_t_1 = preceding_vehicle_velocity
            pass
        # print('approximate velocity: ', self.velocity_t_1.length() * (1 /SCALE_FACTOR))
        pass

    
    
    def get_speed(self):
        return self.velocity_t_1.length() * (1 /SCALE_FACTOR)
    
    def is_set(self):
        return self.tracked_vehicle_id is not None
    
    def get_distance(self):
        return (self.location_t_1 - self.ego_location_t_1).length()

    def get_agent_id(self):
        return self.tracked_vehicle_id

    def get_location(self):
        return self.location_t_1
    
    

    # def check_consistency(self, ego_vehicle, del_t):
    #     self.ego_location_t_2 = self.ego_location_t_1
    #     self.ego_location_t_1 = ego_vehicle.get_location()
        
    #     self.previous_delta_t = del_t

    #     instant_velocity = (self.ego_location_t_1 - self.ego_location_t_2) / del_t

    #     ins_val = instant_velocity.length()

    #     act_val = max(0.1, self.previous_ego_speed)
    #     # act_val = ego_vehicle.get_velocity().length()

    #     diff = ins_val - act_val
    #     ratio = ins_val / act_val
    #     ratio_diff = ratio - self.prev_ratio
    #     self.prev_ratio = ratio

    #     print('val diff: ', diff, 'ratio: ', ratio, 'ratio diff: ', ratio_diff)
    #     self.previous_ego_speed = ego_vehicle.get_velocity().length()