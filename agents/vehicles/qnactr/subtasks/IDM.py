import math
import carla 
TIME_STEP = 1



# class DriverModel(object):

#     @staticmethod
#     def calc_acceleration(vehicle):
#         raise NotImplementedError()

#     @staticmethod
#     def calc_velocity(vehicle):
#         raise NotImplementedError()

#     @staticmethod
#     def calc_position(vehicle):
#         raise NotImplementedError()

#     @staticmethod
#     def calc_gap(vehicle):
#         raise NotImplementedError()


class IDM():

    def __init__(self, parameters_dict, local_map):
        if parameters_dict is None:
            print('IDM.__init__(): parameters_dict is None')
            return

        self.desired_velocity = parameters_dict["desired_velocity"]
        self.safe_time_headway = parameters_dict["safe_time_headway"]
        self.max_acceleration = parameters_dict["max_acceleration"]
        self.comfort_deceleration = parameters_dict["comfort_deceleration"]
        self.acceleration_exponent = parameters_dict["acceleration_exponent"]
        self.minimum_distance = parameters_dict["minimum_distance"]
        self.vehicle_length = parameters_dict["vehicle_length"]

        self.far_distance = 100.0

        self.local_map = local_map
        # self.vehicle = self.local_map.vehicle
        # self.vehicle_velocity = math.sqrt(self.vehicle.get_velocity().squared_length())
        pass

    def calc_acceleration(self):
        """
        dv(t)/dt = [1 - (v(t)/v0)^4  - (s*(t)/s(t))^2]
        """
        vehicle_velocity = self.vehicle_velocity2D()

        gap = 9999
        vehicle_location = self.local_map.vehicle.get_location()
        vehicle_location = carla.Vector3D(vehicle_location.x, vehicle_location.y, 0)
        if self.local_map.vehicle_at_front is not None:
            vehicle_location_at_front = self.local_map.vehicle_at_front.get_location()
            vehicle_location_at_front = carla.Vector3D(vehicle_location_at_front.x, vehicle_location_at_front.y, 0)
            distance = vehicle_location_at_front - vehicle_location
            gap = distance.length()
            

        acceleration = math.pow((vehicle_velocity / self.desired_velocity), 4)
        deceleration = math.pow(self.calc_desired_gap() / min(self.far_distance, gap), 2)

        ret = float(self.max_acceleration * (1 - acceleration - deceleration))
        return ret

    def vehicle_velocity2D(self):
        vehicle_velocity = self.local_map.vehicle.get_velocity()
        vehicle_velocity = carla.Vector3D(vehicle_velocity.x, vehicle_velocity.y, 0)
        vehicle_velocity = math.sqrt(vehicle_velocity.squared_length())
        return vehicle_velocity

    def calc_desired_gap(self):
        pv = self.vehicle_velocity2D()
        if self.local_map.vehicle_at_front:
            lpv = math.sqrt(self.local_map.vehicle_at_front.get_velocity().squared_length())
        else:
            lpv = pv
        
        del_v = (pv - lpv)
        ab = self.max_acceleration * self.comfort_deceleration
        c = ((self.safe_time_headway * pv) + ((pv * del_v) / (2 * math.sqrt(ab))))
        ret = float(self.minimum_distance + max(0, c))
        return ret


    def calc_velocity(self):
        new_velocity = self.calc_raw_velocity()
        return float(max(0, new_velocity))


    def calc_raw_velocity(self):
        vehicle_velocity = self.vehicle_velocity2D()
        acceleration = self.calc_acceleration()

        result = float(vehicle_velocity + (acceleration * TIME_STEP))
        return result


    # def calc_position(vehicle):
    #     if IDM.calc_raw_velocity(vehicle) < 0:
    #         new_position = (vehicle.position -
    #                         (0.5 * (math.pow(vehicle.velocity, 2) /
    #                                 IDM.calc_acceleration(vehicle))))
    #     else:
    #         new_position = (vehicle.position +
    #                         (vehicle.velocity * TIME_STEP) +
    #                         (0.5 * IDM.calc_acceleration(vehicle) *
    #                          math.pow(TIME_STEP, 2)))
    #     return float(new_position)


    # def calc_gap(vehicle):
    #     if vehicle.lead_vehicle:
    #         return float(vehicle.lead_vehicle.position -
    #                      IDM.calc_position(vehicle) -
    #                      vehicle.lead_vehicle.length)
    #     else:
    #         return float(ROAD_LENGTH + 100)


# class TruckPlatoon(DriverModel):
#     @staticmethod
#     def calc_acceleration(vehicle):
#         if vehicle.is_leader:
#             return float(IDM.calc_acceleration(vehicle))
#         else:
#             return float(TruckPlatoon.calc_acceleration(vehicle.lead_vehicle))

#     @staticmethod
#     def calc_velocity(vehicle):
#         if vehicle.is_leader:
#             return float(IDM.calc_velocity(vehicle))
#         else:
#             return float(TruckPlatoon.calc_velocity(vehicle.lead_vehicle))

#     @staticmethod
#     def calc_position(vehicle):
#         if vehicle.is_leader:
#             return float(IDM.calc_position(vehicle))
#         else:
#             return float(TruckPlatoon.calc_position(vehicle.lead_vehicle) -
#                          vehicle.lead_vehicle.length - vehicle.follow_distance)

#     @staticmethod
#     def calc_gap(vehicle):
#         if vehicle.lead_vehicle:
#             return float(vehicle.lead_vehicle.position -
#                          TruckPlatoon.calc_position(vehicle) -
#                          vehicle.lead_vehicle.length)
#         else:
#             return float(ROAD_LENGTH + 100)