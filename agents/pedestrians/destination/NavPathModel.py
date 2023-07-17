
import carla
from shapely.geometry import Polygon, LineString
from agents.pedestrians.soft.LaneSection import LaneSection

from agents.pedestrians.soft.NavPath import NavPath
from ..PedestrianAgent import PedestrianAgent
from agents.pedestrians.factors import InternalFactors
from lib import Geometry, Utils
from .CrosswalkGeometry import CrosswalkGeometry
import numpy as np
from agents.pedestrians.destination.CrosswalkModel import CrosswalkModel


class NavPathModel(CrosswalkModel):
    
    def __init__(
            self, 
            agent: PedestrianAgent, 
            internalFactors: InternalFactors, 
            source: carla.Location, 
            idealDestination: carla.Location, 
            navPath: NavPath,
            areaPolygon: Polygon=None, 
            goalLine: LineString=None,
            debug=True
        ):

        super().__init__(
            agent=agent, 
            internalFactors=internalFactors, 
            source=source, 
            idealDestination=idealDestination, 
            areaPolygon=areaPolygon, 
            goalLine=goalLine,
            debug=debug
        )

        self.navPath = navPath
        self.finalDestination = idealDestination
        self.__initNavigation()

    
        
    def __initNavigation(self):

        # Assume the vehicle is at the right initial position and ped is at the sidewalk.

        vehicle = self.agent.actorManager.nearestOncomingVehicle()
        if vehicle is None:
            return
        
        vehicleWp: carla.Waypoint = self.agent.map.get_waypoint(vehicle.location)
        vehicleRightVector = vehicleWp.transform.get_right_vector()
        vehicleLeftVector = -1 * vehicleRightVector
        
        distanceToVehicle = self.agent.actorManager.distanceFromNearestOncomingVehicle()

        self.intermediatePoints = []
        
        # get nav points which 
        for i, navPoint in enumerate(self.navPath.path):
            # translate navPoints
            # 1. find the waypoint that is navPoint.distanceToEgo infront/back
            if navPoint.isInFrontOfEgo():
                wpOnVehicleLane = vehicleWp.next(navPoint.distanceToEgo)
            else:
                wpOnVehicleLane = vehicleWp.previous(navPoint.distanceToEgo)

            # how many lanes away
            # just assume 2-lane for now
            if navPoint.isOnEgosLeft():
                nearestWP = wpOnVehicleLane.get_left_lane()
            elif navPoint.isOnEgosRight():
                nearestWP = wpOnVehicleLane.get_right_lane()
            else:
                nearestWP = wpOnVehicleLane
            
            # this is also broken
            midLoc = nearestWP.transform.location
            navLoc = midLoc
            if navPoint.laneSection == LaneSection.LEFT:
                navLoc += vehicleLeftVector * nearestWP.lane_width * 0.33
            elif navPoint.laneSection == LaneSection.RIGHT:
                navLoc += vehicleRightVector * nearestWP.lane_width * 0.33
            

            self.intermediatePoints.append(navLoc)
                
        self.nextIntermediatePointIdx = 0
        self.finalDestination = self.intermediatePoints[-1]

        if self.debug:
            # self.visualizer.drawPoints(self.intermediatePoints, life_time=5.0)
            self.visualizer.drawWalkerNavigationPoints(self.intermediatePoints, size=0.1, z=1.0, color=(0, 255, 255), coords=False, life_time=15.0)
