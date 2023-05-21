
import carla

# main issue is we dont have velocity visible for the agent, so we need to calculate it
# so we update velcoity when we see vehicle twice
# each update make corresponding boolean true    

class WorkingMemory():

    def __init__(self):

        self.tracked_vehicle_id = None
        self.threshold_multiplier = 0.05

        self.location_t_1 = carla.Vector3D()
        self.location_t_2 = carla.Vector3D()
        self.velocity_t_1 = carla.Vector3D()

        self.ego_location_t_1 = None
        self.ego_velocity_t_1 = None
        
        self.is_first_update = False
        
        self.tick_passed_since_last_update = 0
        pass
    
    # at least take two observation to calculate the velocity
    def update(self, ego_vehicle, other_vehicle, del_t):
        
        location_t = None
        velocity_t = None
        #  this checks we don't update velocity unless we have both t_1 and t_2
        if self.is_first_update:
            if other_vehicle is None:
                return
            location_t = other_vehicle.get_location()
            self.is_first_update = False
            self.location_t_1 = location_t
        else:
            if other_vehicle is None:
                self.tick_passed_since_last_update += 1
                location_t = self.location_t_1 + self.velocity_t_1 * del_t
                velocity_t = self.velocity_t_1
            else:
                location_t = other_vehicle.get_location()
                velocity_t = (location_t - self.location_t_1) / del_t
                if self.tick_passed_since_last_update != 0:
                    diff = velocity_t - self.velocity_t_1
                    mul = self.tick_passed_since_last_update * self.threshold_multiplier
                    if diff.length() > mul:
                        diff = diff.make_unit_vector() * mul
                    velocity_t = self.velocity_t_1 + diff
                    self.tick_passed_since_last_update = 0
            
            self.location_t_2 = self.location_t_1
            self.location_t_1 = location_t
            self.velocity_t_1 = velocity_t
        self.ego_location_t_1 = ego_vehicle.get_location()
        self.ego_velocity_t_1 = ego_vehicle.get_velocity()
        
        # print('L t-1 ', self.location_t_1, ' L t-2 ', self.location_t_2, ' V t-1 ', self.velocity_t_1)

    # while setting the speed of the vehicle we set the initial speed of the vehicle as ego speed
    def set_agent(self, other_vehicle, ego_vehicle):
        self.tracked_vehicle_id = other_vehicle.id
        # self.velocity_t_1 = ego_vehicle.get_velocity()    # assumption
        self.location_t_2 = other_vehicle.get_location()
        
        self.ego_location_t_1 = ego_vehicle.get_location()
        self.ego_velocity_t_1 = ego_vehicle.get_velocity()
        
        self.is_first_update = True
        print('agent set ')
        pass
    
    def get_speed(self):
        if self.velocity_t_1.length() == 0:
            return self.ego_velocity_t_1.length()
        return self.velocity_t_1.length() 
    
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
    
    
    
    
    
    
    # types of parameters:
    # # ego_velocity: carla.Vector3D
    # # other_vehicle: carla.Vehicle
    # # del_t: float
    # # we work with only location data 
    # # we approximate velocity from the ego location data
    # def update(self, ego_vehicle, other_vehicle, del_t):
    #     # print('update', ego_vehicle, other_vehicle, del_t)
    #     location_t = None
    #     preceding_vehicle_velocity = None
    #     # we have not created the working memory yet when previous_ego_velocity is None
    #     if self.previous_ego_velocity is None:
    #         self.previous_ego_velocity = ego_vehicle.get_velocity()
    #         pass
    #     # we have a tracked vehicle where driver is looking at 
    #     # so actual update
    #     if other_vehicle is not None:
    #         print('actual update')
    #         self.tracked_vehicle_id = other_vehicle.id
    #         location_t = other_vehicle.get_location()
    #     else:
    #         # other vehicle is none; can happen for one resons:
    #         # 1. we are updating the working memory with dead reconing 
    #         print('approximate update')
    #         # chekcing if we were tracking a vehicle before
    #         if self.tracked_vehicle_id is None:
    #             #  we are not tracking a vehicle before and no vehicle came as other vehicle
    #             location_t = ego_vehicle.get_location() + 100 * ego_vehicle.get_velocity().make_unit_vector()
    #             self.location_t_1 = ego_vehicle.get_location() + 99 * ego_vehicle.get_velocity().make_unit_vector()
    #             pass
    #         else:
    #             preceding_vehicle_velocity = (self.location_t_1 - self.location_t_2) / del_t
    #             diff_velocity = preceding_vehicle_velocity - self.previous_ego_velocity
    #             location_t = self.location_t_1 + diff_velocity * del_t

        
    #     self.location_t_2 = self.location_t_1
    #     self.location_t_1 = location_t 
    #     self.previous_ego_velocity = ego_vehicle.get_velocity()
    #     self.ego_location_t_1 = ego_vehicle.get_location()

    #     if preceding_vehicle_velocity is None:
    #         self.velocity_t_1 = (self.location_t_1 - self.location_t_2) / del_t
    #         pass
    #     else:
    #         self.velocity_t_1 = preceding_vehicle_velocity
    #         pass
        
    #     # print(f'tracked id {self.tracked_vehicle_id}')
    #     # print(f'ego loc {self.ego_location_t_1}, vel {self.previous_ego_velocity}')
    #     print(f'tracked id {self.tracked_vehicle_id} loc (t-1){self.location_t_1}, (t-2){self.location_t_2} vel(t-1) {self.velocity_t_1}')
        
    #     pass