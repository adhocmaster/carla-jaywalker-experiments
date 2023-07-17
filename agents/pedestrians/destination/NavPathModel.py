
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


class NavPathModel():
    
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
        self.internalFactors = internalFactors

        self.debug = debug
        self.visualizer = agent.visualizer
        self.agent = agent
        self.source = source
        self.idealDestination = idealDestination
        self.areaPolygon = areaPolygon
        self.goalLine = goalLine

        self.crosswalkGeometry = None
        self.intermediatePoints = []
        self.finalDestination = None
        self.nextIntermediatePointIdx = None
        self.navPath = navPath
        self.finalDestination = idealDestination
        self.initialized = False
        self.initNavigation()

    def getFinalDestination(self):
        return self.finalDestination
    
    def initNavigation(self):

        # Assume the vehicle is at the right initial position and ped is at the sidewalk.

        if self.initialized:
            return

        vehicle = self.agent.actorManager.nearestOncomingVehicle
        if vehicle is None:
            self.agent.logger.warning("No oncoming vehicle found")
            # exit(0)
            return
        
        vehicleWp: carla.Waypoint = self.agent.map.get_waypoint(vehicle.get_location())
        vehicleRightVector = vehicleWp.transform.get_right_vector()
        vehicleLeftVector = -1 * vehicleRightVector
        
        distanceToVehicle = self.agent.actorManager.distanceFromNearestOncomingVehicle()

        # TODO, this is not correct as the first nav point might be inside a road.
        firstNavPoint = self.navPath.path[0]
        if distanceToVehicle > firstNavPoint.distanceToInitialEgo:
            return

        self.intermediatePoints = []
        
        # get nav points which 
        for i, navPoint in enumerate(self.navPath.path):
            # translate navPoints
            # 1. find the waypoint that is navPoint.distanceToEgo infront/back
            wpOnVehicleLane = vehicleWp.next(navPoint.distanceToInitialEgo)[0]
            # if navPoint.isInFrontOfEgo():
            #     wpOnVehicleLane = vehicleWp.next(navPoint.distanceToInitialEgo)[0]
            # else:
            #     wpOnVehicleLane = vehicleWp.previous(navPoint.distanceToInitialEgo)[0]
            vehicleRightVector = wpOnVehicleLane.transform.get_right_vector()
            vehicleLeftVector = -1 * vehicleRightVector
            print("vehicleRightVector", vehicleRightVector)
            print("vehicleLeftVector", vehicleLeftVector)

            print(f"navpoint {i} wpOnVehicleLane: {wpOnVehicleLane} with road id = {wpOnVehicleLane.road_id}, lane id = {wpOnVehicleLane.lane_id}")
            # how many lanes away
            # just assume 2-lane for now
            if navPoint.laneId == 0:
                nearestWP = wpOnVehicleLane
            elif navPoint.isOnEgosLeft():
                nearestWP = wpOnVehicleLane.get_left_lane()
                print(f"navpoint {i} on the left")
            elif navPoint.isOnEgosRight():
                print(f"navpoint {i} on the right")
                nearestWP = wpOnVehicleLane.get_right_lane()
                
            print(f"nearestWP: {nearestWP}")

            self.visualizer.drawPoint(nearestWP.transform.location, size=0.1, color=(255,0,0,100), life_time = 15.5)
            
            # this is also broken
            midLoc = nearestWP.transform.location
            navLoc = midLoc
            if navPoint.laneSection == LaneSection.LEFT:
                navLoc += vehicleLeftVector * nearestWP.lane_width * 0.33
            elif navPoint.laneSection == LaneSection.RIGHT:
                navLoc += vehicleRightVector * nearestWP.lane_width * 0.33
            

            self.intermediatePoints.append(navLoc)
                
        self.nextIntermediatePointIdx = 0
        self.intermediatePoints.append(self.finalDestination)

        self.initialized = True

        if self.debug:
            # self.visualizer.drawPoints(self.intermediatePoints, life_time=5.0)
            self.visualizer.drawWalkerNavigationPoints(self.intermediatePoints, size=0.1, z=1.0, color=(0, 255, 255), coords=False, life_time=60.0)

    def getNextDestinationPoint(self):

        if len(self.intermediatePoints) == 0:
            return self.finalDestination
        # TODO
        # find if the pedestrian reached the local y coordinate with a threshold around 100 cm
        # change next destination point to the next intermediate point return 
        if self.hasReachedNextDestinationPoint(self.agent.location):
            if self.nextIntermediatePointIdx == len(self.intermediatePoints) - 1:
                self.agent.logger.info(f"going to the final destination")
                d =  self.agent.location.distance_2d(self.finalDestination)
                self.agent.logger.info(f"distance to next destination {d} meters")
                return self.finalDestination
            self.nextIntermediatePointIdx += 1 # this might overflow if we have reached the final 
        
        return self.intermediatePoints[self.nextIntermediatePointIdx]

    
    def hasReachedNextDestinationPoint(self, agentLocation: carla.Location):
        # TODO: fill it out
        nextDest = self.intermediatePoints[self.nextIntermediatePointIdx]

        return self.agent.hasReachedDestinationAlongLocalY(nextDest, 0.5)