import carla
from typing import List, Tuple
from .Geometry import Geometry

class RoadHelper:

    @staticmethod
    def getPlayerWP(map: carla.Map, player: carla.Vehicle) -> carla.Waypoint:
        
        playerLocation = player.get_location()
        playerWP = map.get_waypoint(
            playerLocation,
            project_to_road=True
            )
        return playerWP

    @staticmethod
    def areWPsOnTheSameLane(wp1: carla.Waypoint, wp2: carla.Waypoint) -> bool:
        # TODO: This method will return incorrect results when different lane numbers are connected to each other, which can happen at lane section transition
        return wp1.lane_id == wp2.lane_id
    
    @staticmethod
    def getWaypointOnTheLeft(map: carla.Map, wp: carla.Waypoint) -> carla.Waypoint:
        
        transform = wp.transform
        
        rightVector = transform.get_right_vector().make_unit_vector()
        leftVector = rightVector * -1
        point = transform.location + leftVector * 3
        leftWP = map.get_waypoint(
            point,
            project_to_road=True
        )

        if RoadHelper.areWPsOnTheSameLane(wp, leftWP):
            return None

        return leftWP

    @staticmethod
    def getWaypointOnTheRight(map: carla.Map, wp: carla.Waypoint) -> carla.Waypoint:
        
        transform = wp.transform
        
        rightVector = transform.get_right_vector().make_unit_vector()
        point = transform.location + rightVector * 3
        rightWP = map.get_waypoint(
            point,
            project_to_road=True
        )

        if RoadHelper.areWPsOnTheSameLane(wp, rightWP):
            return None

        return leftWP
    
    @staticmethod
    def getWPsInFront(wp: carla.Waypoint, distance, steps=1) -> List[carla.Waypoint]:
        wps = []

        for i in range(1, steps + 1):
            wps.extend(wp.next(distance * i))

        return wps
    
    @staticmethod
    def getWPsBehind(wp: carla.Waypoint, distance, steps=1) -> List[carla.Waypoint]:
        wps = []

        for i in range(1, steps + 1):
            wps.extend(wp.previous(distance * i))

        return wps

    
    @staticmethod
    def getWalkerSpawnPointsInFront(world: carla.World, vehicle: carla.Vehicle) -> Tuple[List[carla.Transform], List[carla.Transform]]:

        vehicleWp = RoadHelper.getPlayerWP(world.get_map(), vehicle)
        frontWps = RoadHelper.getWPsInFront(vehicleWp, 10, steps=5)

        leftSpawnPoints = []
        rightSpawnPoints = []

        for wp in frontWps:
            leftSidewalkLocation, rightSidewalkLocation = RoadHelper.getSideWalkLocations(world, wp)
            if leftSidewalkLocation is not None:
                leftSpawnPoints.append(carla.Transform(location = leftSidewalkLocation))
            if rightSidewalkLocation is not None:
                rightSpawnPoints.append(carla.Transform(location = rightSidewalkLocation))
        
        return leftSpawnPoints, rightSpawnPoints
        

    @staticmethod
    def getSideWalkLocations(world: carla.World, wp: carla.Waypoint) -> Tuple[carla.Location, carla.Location]:
        """This is a naive approach and will not work well where the lane and the sidewalks do not run parallel; 
        There are edge case where left and right points are not on the shorted crossing path. We need to find them in another approach

        Args:
            world (carla.World): _description_
            wp (carla.Waypoint): _description_

        Returns:
            Tuple[carla.Location, carla.Location]: point on the left and on the right sidewalks.
        """
        # make a scanline towards the left
        # Geometry.getSideWalkPointOnScanLine

        rightVector = wp.transform.get_right_vector().make_unit_vector()
        leftVector = rightVector * -1

        aPointOnTheRight = rightVector * 20 + wp.transform.location
        aPointOnTheLeft = leftVector * 20 +  wp.transform.location

        scanLine = Geometry.makeCenterScanLine(wp.transform.location, aPointOnTheLeft)
        leftSidewalkPoint = Geometry.getSideWalkPointOnScanLine(scanLine)

        scanLine = Geometry.makeCenterScanLine(wp.transform.location, aPointOnTheRight)
        rightSidewalkPoint = Geometry.getSideWalkPointOnScanLine(scanLine)

        # there are edge case where left and right points are not on the shorted crossing path. We need to find them in another approach

        return Geometry.pointtoLocation(leftSidewalkPoint), Geometry.pointtoLocation(rightSidewalkPoint)

