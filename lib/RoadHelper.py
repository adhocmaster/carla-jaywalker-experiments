import carla


class RoadHelper:

    @staticmethod
    def areWPsOnTheSameLane(wp1: carla.Waypoint, wp2: carla.Waypoint) -> bool:
        # TODO: This method will return incorrect results when different lane numbers are connected to each other, which can happen at lane section transition
        return wp1.lane_id == wp2.lane_id
    
    @staticmethod
    def getWaypointOnTheLeft(map: carla.Map, wp: carla.Waypoint):
        
        transform = wp.get_transform()
        
        rightVector = transform.get_right_vector().make_unit_vector()
        leftVector = - rightVector
        point = transform.location + leftVector * 3
        leftWP = self.map.get_waypoint(
            point,
            project_to_road=True
        )

        if RoadHelper.areWPsOnTheSameLane(wp, leftWP):
            return None

        return leftWP

    @staticmethod
    def getWaypointOnTheRight(map: carla.Map, wp: carla.Waypoint):
        
        transform = wp.get_transform()
        
        rightVector = transform.get_right_vector().make_unit_vector()
        point = transform.location + rightVector * 3
        rightWP = self.map.get_waypoint(
            point,
            project_to_road=True
        )

        if RoadHelper.areWPsOnTheSameLane(wp, rightWP):
            return None

        return leftWP
    
    @staticmethod
    def getForwardWPs(map, wp: carla.Waypoint, distance, steps=1):
        wps = []

        for i in range(steps):
            wps.append(wp.next(distance * i))
