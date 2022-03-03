import carla
from abc import ABC
from lib import WaypointTooFar


class PedUtils(ABC):

    def getNearestDrivingWayPointAndDistance(map, agentLocation):
        waypoint = map.get_waypoint(agentLocation)
        distance = agentLocation.distance_2d(waypoint.transform.location)
        if distance > 10:
            raise WaypointTooFar(f"Distance to nearest waypoint {distance}")\
        
        return waypoint, distance
        

    
    def getLaneWidth(waypoint: carla.Waypoint):
        return waypoint.lane_width

    
    def timeToCrossNearestLane(map, agentLocation, speed):
        """Assumes pedestrian will cross with desired speed.

        """
        nearestWp, dToWp = PedUtils.getNearestDrivingWayPointAndDistance(map, agentLocation)
        # TTX = agent.internalFactors["desired_speed"] * dToWp + (PedUtils.getLaneWidth() / 2)
        # TTX = speed * dToWp + (PedUtils.getLaneWidth(nearestWp) / 2)
        TTX = (dToWp +  (PedUtils.getLaneWidth(nearestWp) / 2)) / speed
        return TTX
    
    def timeToReachNearestWP(map, agentLocation, speed):
        """Assumes pedestrian will cross with desired speed.

        """
        nearestWp, dToWp = PedUtils.getNearestDrivingWayPointAndDistance(map, agentLocation)
        # TTX = agent.internalFactors["desired_speed"] * dToWp + (PedUtils.getLaneWidth() / 2)
        # TTX = speed * dToWp + (PedUtils.getLaneWidth(nearestWp) / 2)
        TTX = dToWp/ speed
        return TTX