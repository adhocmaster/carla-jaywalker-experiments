
from typing import Dict, Optional
import carla
from lib.LoggerFactory import LoggerFactory
from shapely.geometry import Polygon, LineString
from agents.pedestrians.planner.DynamicBehaviorModelFactory import DynamicBehaviorModelFactory
from agents.pedestrians.soft import BehaviorMatcher, Direction, NavPoint
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
        self.finalDestination = idealDestination

        self.logger = LoggerFactory.create(f"NavPathModel #{self.agent.id}")


        self.intermediatePointsToNavPointMap: Dict[carla.Location, NavPoint] = {}
        self.navPath = navPath
        self.initialized = False
        self.dynamicBehaviorModelFactory = DynamicBehaviorModelFactory()
        matcher = BehaviorMatcher()
        matcher.tagNavPoints(self.navPath)
        

        # for idx, navPoint in enumerate(self.navPath.path):
        #     print("\n")
        #     print("nav idx:", idx)
        #     print(navPoint)
        #     print(id(navPoint.behaviorTags))
        # raise Exception("stop here")
        self.initNavigation()

    def getFinalDestination(self):
        return self.finalDestination
    
    def setFinalDestination(self, destination):
        self.finalDestination = destination
    

    def __canStart(self) -> bool:
        """Conditions
        1. There must be an oncoming vehicle
        2. The oncoming vehicle must be within a certain distance


        Returns:
            bool: _description_
        """
        vehicle = self.agent.actorManager.nearestOncomingVehicle
        if vehicle is None:
            return False
        
        return True
        
        # distanceToVehicle = self.agent.actorManager.distanceFromNearestOncomingVehicle()
        # # TODO, this is not correct as the first nav point might be inside a road.
        # firstNavPoint = self.navPath.path[0]
        # if distanceToVehicle > firstNavPoint.distanceToInitialEgo:
        #     return False
        
        # return True
        


    def isDone(self):
        return ((self.initialized)
            and (len(self.intermediatePoints) > len(self.navPath.path))
            and (self.intermediatePoints[self.nextIntermediatePointIdx] == self.finalDestination)
            )

    
    def initNavigation(self):

        # Assume the vehicle is at the right initial position and ped is at the sidewalk.
        # print("initalizing navigation path")

        if self.initialized:
            return
        
        if not self.__canStart():
            return

        vehicle = self.agent.actorManager.egoVehicle
        
        vehicleWp: carla.Waypoint = self.agent.map.get_waypoint(vehicle.get_location())
        vehicleRightVector = vehicleWp.transform.get_right_vector()
        vehicleLeftVector = -1 * vehicleRightVector
        


        self.intermediatePoints = []
        
        # get nav points which 
        prevNavPoint = None
        for i, navPoint in enumerate(self.navPath.path):
            # translate navPoints
            # 1. find the waypoint that is navPoint.distanceToEgo infront/back
            vehicleConflictWp = vehicleWp.next(navPoint.distanceToInitialEgo * 1.5)[0] # add extent
            # we need to translate wpOnVehicleLane wrt the initial start point on the sidewalk
          
            navLoc = self.getNavPointLocation(navPoint, vehicleConflictWp, prevNavPoint)

            # print("navLoc", navLoc)
            self.intermediatePoints.append(navLoc)
            self.intermediatePointsToNavPointMap[navLoc] = navPoint
            prevNavPoint = navPoint
        
                
        self.nextIntermediatePointIdx = 0
        self.intermediatePoints.append(self.finalDestination)

        self.initialized = True

        if self.debug:
            # self.visualizer.drawPoints(self.intermediatePoints, life_time=5.0)
            self.visualizer.drawWalkerNavigationPoints(self.intermediatePoints, size=0.075, z=0.25, color=(0, 255, 255), coords=False, life_time=15.0)
        self.agent.world.tick()
        # raise Exception("stop here")

    
    def getNavWaypoint(self, navPoint: NavPoint, vehicleConflictWp: carla.Waypoint) -> Optional[carla.Waypoint]:
        """_summary_

        Args:
            navPoint (NavPoint): _description_
            vehicleConflictWp (carla.Waypoint): _description_

        Returns:
            Optional[carla.Waypoint]: It can return None if the nav point lane does not exist in the current road or there is a issue in the map.
        """

        # TODO just assume 2-lane for now
        nearestWP = vehicleConflictWp
        if navPoint.isOnEgosLeft():
            laneOffset = -navPoint.laneId 
            # print(laneOffset)
            for i in range(laneOffset):
                if (Utils.wayPointsSameDirection(nearestWP, vehicleConflictWp)):
                    nearestWP = nearestWP.get_left_lane()
                else:
                    nearestWP = nearestWP.get_right_lane()
                    
                # print(nearestWP, nearestWP.lane_id, nearestWP.road_id) # does not work as the orientation of left and right is changed based on the driving direction.
            # print(f"navpoint {i} on the left")
        elif navPoint.isOnEgosRight():
            laneOffset = navPoint.laneId 
            # print(f"navpoint {i} on the right")
            for i in range(laneOffset):
                if (Utils.wayPointsSameDirection(nearestWP, vehicleConflictWp)):
                    nearestWP = nearestWP.get_right_lane()
                else:
                    nearestWP = nearestWP.get_left_lane()
        
        # print(f"nearestWP: {nearestWP}")

        return nearestWP
    
    def getNavPointLocation(self, navPoint: NavPoint, vehicleConflictWp: carla.Waypoint, prevNavPoint: Optional[NavPoint]) -> carla.Location:
            vehicleRightVector = vehicleConflictWp.transform.get_right_vector()
            vehicleLeftVector = -1 * vehicleRightVector
            # print("vehicleRightVector", vehicleRightVector)
            # print("vehicleLeftVector", vehicleLeftVector)
            navWP = self.getNavWaypoint(navPoint, vehicleConflictWp)
            if navWP is None:
                raise Exception(f"nearestWP is None for navPoint {navPoint}")
            
            overlapMigitationOffset = 0.0
            if prevNavPoint is not None:
                if navPoint.isAtTheSameLocation(prevNavPoint):
                    # we need to add some offset
                    # if self.navPath.direction == Direction.LR:
                    navPoint.overlapOffset = 0.05 + prevNavPoint.overlapOffset
            
            # print("navPoint.overlapOffset", navPoint.overlapOffset)
            # this is also broken
            midLoc = navWP.transform.location
            navLoc = midLoc
            if navPoint.laneSection == LaneSection.LEFT:
                navLoc += vehicleLeftVector * navWP.lane_width * 0.33 
            elif navPoint.laneSection == LaneSection.RIGHT:
                navLoc += vehicleRightVector * navWP.lane_width * 0.33 
            
            if navPoint.overlapOffset > 0:
                if self.navPath.direction == Direction.LR:
                    navLoc += vehicleRightVector * navWP.lane_width * navPoint.overlapOffset
                else:
                    navLoc += vehicleLeftVector * navWP.lane_width * navPoint.overlapOffset

            return navLoc


                


    def getNextDestinationPoint(self):

        if len(self.intermediatePoints) == 0:
            return self.finalDestination
        # TODO
        # find if the pedestrian reached the local y coordinate with a threshold around 100 cm
        # change next destination point to the next intermediate point return 
        if self.hasReachedNextDestinationPoint():
            if self.nextIntermediatePointIdx == len(self.intermediatePoints) - 1:
                self.agent.logger.info(f"going to the final destination")
                d =  self.agent.location.distance_2d(self.finalDestination)
                self.agent.logger.info(f"distance to next destination {d} meters")
                return self.finalDestination
            self.nextIntermediatePointIdx += 1 # this might overflow if we have reached the final 
        
        return self.intermediatePoints[self.nextIntermediatePointIdx]
    

    def activateBehaviorModels(self):
        """Activates behavior models slightly before the agent reaches the next nav point.
        """
        nextDest = self.intermediatePoints[self.nextIntermediatePointIdx]
        navPoint = self.intermediatePointsToNavPointMap[nextDest]
        self.logger.debug(f"has reached nav point {navPoint}")
        for behaviorType in navPoint.behaviorTags:
            # print(navPoint)
            self.logger.warn(f"Tick {self.agent.currentEpisodeTick} : reached nav point {self.nextIntermediatePointIdx}. activating behavior {behaviorType}")
            # self.agent.visualizer.drawPoint(nextDest, color=(0, 0, 255), life_time=10.0)
            self.dynamicBehaviorModelFactory.addBehavior(self.agent, behaviorType)

    
    def hasReachedFirstDestinationPoint(self):
        """
        Has a side effect of activating and deactivating forces.
        """
        # TODO: fill it out
        nextDest = self.intermediatePoints[self.nextIntermediatePointIdx]

        hasReached = self.agent.hasReachedDestinationAlongLocalY(nextDest, 0.5)

        if hasReached and nextDest in self.intermediatePointsToNavPointMap:
            # activate the models required for the nav point
            self.activateBehaviorModels()

        return hasReached
    

    def hasReachedNextDestinationPoint(self):
        if self.nextIntermediatePointIdx == 0:
            return self.hasReachedFirstDestinationPoint()
        
        prevDest = self.intermediatePoints[self.nextIntermediatePointIdx - 1]
        nextDest = self.intermediatePoints[self.nextIntermediatePointIdx]

        # print("prevDest", prevDest)
        # print("nextDest", nextDest)
        destDirection = (nextDest - prevDest).make_unit_vector() # might be 0 if both nav points are at the same location
        destinationVec = nextDest - prevDest

        if self.distanceToNextDestination() < 0.25: # 0.25 meters close
            self.activateBehaviorModels()
            return True
        
        # overshoot check
        overshoot = (self.agent.location - prevDest).dot(destDirection) - destinationVec.length()
        if overshoot > -0.25:
            self.activateBehaviorModels()
            return True
        
        return False
    

    def distanceToNextDestination(self):
        nextDest = self.intermediatePoints[self.nextIntermediatePointIdx]
        progressVec = nextDest - self.agent.location
        return progressVec.length()



        
    
    
    def calculateForce(self) -> Optional[carla.Vector3D]:
        """May not return force if not needed.

        Returns:
            _type_: _description_
        """

        # first we do a sideeffect of updating the behavior models based on the current nav point.

        desiredVelocity = self.getAverageVelocityRequiredToReachNext()
        if desiredVelocity is None: # let the destination model handle it
            return None
        oldVelocity = self.agent.getOldVelocity()

        requiredChangeInVelocity = (desiredVelocity - oldVelocity)

        # self.visualizer.visualizeForces(
        #     "velocities", 
        #     {"desiredVelocity": desiredVelocity, "oldVelocity": oldVelocity}, 
        #     self.agent.visualizationForceLocation, 
        #     self.agent.visualizationInfoLocation
        # )

        # if very close to the next destination, invert the force
        
        force = requiredChangeInVelocity / 0.01 #instant change

        # if self.distanceToNextDestination() < 0.5:
        #     force = -1 * force

        return force
        
    
    def getAverageVelocityRequiredToReachNext(self) -> Optional[carla.Vector3D]:
        """Returns the average velocity required to reach the next intermediate point

        Returns:
            float: average velocity required to reach the next intermediate point
        """
        ## TODO fist check if the vehicle is oncoming or not. Because if the vehicle passed, we don't need to follow the nav path anymore.

        vehicle = self.agent.actorManager.egoVehicle # this is not correct, we need the ego

        if not self.agent.actorManager.isOncoming(vehicle):
            self.agent.logger.warning(f"vehicle is not oncoming. stopping nav path model")
            return None
        
        # print(f"next location id {self.nextIntermediatePointIdx}")
        nextLoc = self.intermediatePoints[self.nextIntermediatePointIdx]

        if nextLoc == self.finalDestination:
            self.agent.logger.warning(f"no intermediate location. stopping nav path model")
            return None

        nextNavPoint = self.navPath.path[self.nextIntermediatePointIdx]

        currentDToVehicle = Utils.distanceToVehicle(nextLoc, vehicle)

        assert currentDToVehicle is not None

        requiredDToVehicle = nextNavPoint.distanceToEgo
        vehicleTravelD = currentDToVehicle - requiredDToVehicle
        if vehicleTravelD < 0:
            # return self.agent.getOldVelocity()
            self.logger.warn(f"vehicleTravelD is negative, it already crossed the threshold: {vehicleTravelD}, currentDToVehicle: {currentDToVehicle}, requiredDToVehicle: {requiredDToVehicle}")
            direction = (nextLoc - self.agent.location).make_unit_vector()
            return 5 * direction # quickly move to the next dest
            # return None
        
        # vehicle may stop
        vehicleSpeed = vehicle.get_velocity().length()
        if vehicleSpeed < 0.1:
            return None
        timeToReachNextNavPoint = vehicleTravelD / vehicleSpeed
        # print("timeToReachNextNavPoint", timeToReachNextNavPoint)
        dToNext = self.agent.location.distance_2d(nextLoc)
        # print("dToNext", dToNext)
        speed = dToNext / timeToReachNextNavPoint
        # print("speed", speed)
        direction = (nextLoc - self.agent.location).make_unit_vector()
        return speed * direction * 1.2
    