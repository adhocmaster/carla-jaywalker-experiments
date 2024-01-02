
import math
from typing import Dict, Optional
import carla
from lib.InteractionUtils import InteractionUtils
from lib.LoggerFactory import LoggerFactory
from shapely.geometry import Polygon, LineString
from agents.pedestrians.planner.DynamicBehaviorModelFactory import DynamicBehaviorModelFactory
from agents.pedestrians.soft import BehaviorMatcher, Direction, NavPoint
from agents.pedestrians.soft.LaneSection import LaneSection

from agents.pedestrians.soft.NavPath import NavPath
from ..PedestrianAgent import PedestrianAgent
from agents.pedestrians.factors import InternalFactors
from lib import Geometry, Utils, VehicleUtils
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
        self.vehicleLaneId = None # need this one to retranslate remaining nav points
        self.vehicleLag = 10 # we add a lag in distance to let the vehicle pick up the speed.
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

    # region initialization

    def reinitializeIfNeeded(self):
        """In case of a change in vehicle driving lane or lane-width, we translate the remaining navLocs
        This method has flaw when lane numbering changes.
        """
        vehicle = self.agent.egoVehicle
        if VehicleUtils.hasVehicleCompletelyChangedLane(self.vehicleLaneId, vehicle):

            V_Ref_Front_Wp = VehicleUtils.getVehicleFrontWp(vehicle)
            newLaneId = V_Ref_Front_Wp.lane_id
            self.navPath.setEgoLaneWrtCenter(abs(newLaneId))
            self.logger.warn(f"vehicle lane has changed from {self.vehicleLaneId} to {newLaneId}. reinitializing nav path model and updating egoWrtCenter.")

            self.rePlaceNavpointsFromIdx(self.nextIntermediatePointIdx + 1)
        pass



    def rePlaceNavpointsFromIdx(self, idx: int):
        """Replaces the nav points from idx to the end of the nav points list"""

        vehicle = self.agent.egoVehicle
        
        V_Ref_Front_Wp = VehicleUtils.getVehicleFrontWp(vehicle)
        V_Ref_Back_Wp = VehicleUtils.getVehicleBackWp(vehicle)

        self.vehicleLaneId = V_Ref_Front_Wp.lane_id

        if idx == 0:
            self.intermediatePoints = []
        else:
            self.intermediatePoints = self.intermediatePoints[:idx] # discarding old ones
        

        prevNavPoint = None
        prevNavLoc = None
        for i, navPoint in enumerate(self.navPath.path):
            if i < idx:
                continue
            # translate navPoints
            # 1. find the waypoint that is navPoint.distanceToEgo infront/back
            if navPoint.distanceToEgo < 0 and navPoint.distanceToInitialEgo < 0:
                vehicleConflictWp = V_Ref_Back_Wp.next(navPoint.distanceToInitialEgo + self.vehicleLag)[0] 
                # vehicleConflictWp = V_Ref_Front_Wp.next(navPoint.distanceToInitialEgo + self.vehicleLag)[0] # initial location is always from the front.
            else:
                vehicleConflictWp = V_Ref_Front_Wp.next(navPoint.distanceToInitialEgo + self.vehicleLag)[0]
          
            navLoc = self.getNavPointLocation(navPoint, vehicleConflictWp, prevNavPoint, prevNavLoc)

            # print("navLoc", navLoc)
            self.intermediatePoints.append(navLoc)
            self.intermediatePointsToNavPointMap[navLoc] = navPoint
            prevNavPoint = navPoint
            prevNavLoc = navLoc
        
                
        self.nextIntermediatePointIdx = idx
        self.intermediatePoints.append(self.finalDestination)


        if self.debug:
            # self.visualizer.drawPoints(self.intermediatePoints, life_time=5.0)
            self.visualizer.drawWalkerNavigationPoints(self.intermediatePoints, size=0.075, z=0.25, color=(0, 255, 255), coords=False, life_time=15.0)
        self.agent.world.tick()
        # raise Exception("stop here")


    def initNavigation(self):

        # Assume the vehicle is at the right initial position and ped is at the sidewalk.
        # print("initalizing navigation path")

        if self.initialized:
            self.reinitializeIfNeeded() 
            return
        
        if not self.__canStart():
            return

        self.logger.warn("NavPathModel will adjust the source and the destination to match the endpoints of the path")

        self.rePlaceNavpointsFromIdx(0)
        self.setWalkersInitialPosition()
        self.setWalkerFinalDestination() # has issues
        self.initialized = True

    
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
            # print("laneOffset", laneOffset)
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
    
    def getNavPointLocation(self, navPoint: NavPoint, vehicleConflictWp: carla.Waypoint, prevNavPoint: Optional[NavPoint], prevLoc: Optional[carla.Location]) -> carla.Location:
            vehicleRightVector = vehicleConflictWp.transform.get_right_vector()
            vehicleLeftVector = -1 * vehicleRightVector
            # print("vehicleRightVector", vehicleRightVector)
            # print("vehicleLeftVector", vehicleLeftVector)
            navWP = self.getNavWaypoint(navPoint, vehicleConflictWp)
            if navWP is None:
                raise Exception(f"nearestWP is None for navPoint {navPoint}")
            
            
            if prevNavPoint is not None:
                if navPoint.isAtTheSameLocation(prevNavPoint):
                    # we need to compute new location based on prevNavPoint Location, not the mid location
                    navPoint.overlapOffset = 0.05 + prevNavPoint.overlapOffset
                    if self.navPath.direction == Direction.LR:
                        navLoc = prevLoc + vehicleRightVector * navWP.lane_width * navPoint.overlapOffset
                    else:
                        navLoc = prevLoc + vehicleLeftVector * navWP.lane_width * navPoint.overlapOffset
                    # print(prevLoc, navLoc)
                    # exit(0)
                    return navLoc
            
            # print("navPoint.overlapOffset", navPoint.overlapOffset)
            # this is also broken
            noise = np.random.uniform(0.8, 1.2) # added for variability
            midLoc = navWP.transform.location
            navLoc = midLoc
            sectionWidth = 0.33

            if navPoint.laneSection == LaneSection.LEFT:
                navLoc = midLoc + vehicleLeftVector * navWP.lane_width * sectionWidth * noise
            elif navPoint.laneSection == LaneSection.RIGHT:
                navLoc = midLoc + vehicleRightVector * navWP.lane_width * sectionWidth * noise
            else:
                # mid noise
                if np.random.choice([True, False]):
                    navLoc = midLoc + vehicleLeftVector * navWP.lane_width * (sectionWidth / 2) * np.random.uniform(0, 0.5)
                else:
                    navLoc = midLoc + vehicleRightVector * navWP.lane_width * (sectionWidth / 2) * np.random.uniform(0, 0.5)
            
            # this is not needed anymore
            # if navPoint.overlapOffset > 0:
            #     if self.navPath.direction == Direction.LR:
            #         navLoc += vehicleRightVector * navWP.lane_width * navPoint.overlapOffset
            #     else:
            #         navLoc += vehicleLeftVector * navWP.lane_width * navPoint.overlapOffset

            # print("vehicleConflictWp", vehicleConflictWp)
            # print("navWP", navWP)
            # print("navLoc", navLoc)

            return navLoc


    def setWalkersInitialPosition(self):
        if len(self.intermediatePoints) == 0:
            return
        
        vehicle = self.agent.egoVehicle
        
        firstNavPoint = self.navPath.path[0]

        if firstNavPoint.distanceToEgo < 0:
            V_Ref_Back_Wp = VehicleUtils.getVehicleBackWp(vehicle)
            vehicleConflictWp = V_Ref_Back_Wp.next(firstNavPoint.distanceToInitialEgo + self.vehicleLag)[0] 
        else:
            V_Ref_Front_Wp = VehicleUtils.getVehicleFrontWp(vehicle)
            vehicleConflictWp = V_Ref_Front_Wp.next(firstNavPoint.distanceToInitialEgo + self.vehicleLag)[0]
        
        firstLoc = self.intermediatePoints[0]
        firstLocWp = self.agent.map.get_waypoint(firstLoc)

        leftSideWalk, rightSidewalk = Utils.getSideWalks(self.agent.world, firstLocWp)

        sidewalk = leftSideWalk
        if Utils.wayPointsSameDirection(firstLocWp, vehicleConflictWp):
            if self.navPath.direction == Direction.LR:
                sidewalk = leftSideWalk
            else:
                sidewalk = rightSidewalk
        else: # opposite direction
            if self.navPath.direction == Direction.LR:
                sidewalk = rightSidewalk
            else:
                sidewalk = leftSideWalk

        self.agent.walker.set_location(sidewalk.location)

    def setWalkerFinalDestination(self):
        if len(self.intermediatePoints) < 2: # last one is the final destination which we need to fix
            return
        
        vehicle = self.agent.egoVehicle
        lastNavPoint = self.navPath.path[-2] # before the final destination

        if lastNavPoint.distanceToEgo < 0:
            V_Ref_Back_Wp = VehicleUtils.getVehicleBackWp(vehicle)
            vehicleConflictWp = V_Ref_Back_Wp.next(lastNavPoint.distanceToInitialEgo + self.vehicleLag)[0] 
        else:
            V_Ref_Front_Wp = VehicleUtils.getVehicleFrontWp(vehicle)
            vehicleConflictWp = V_Ref_Front_Wp.next(lastNavPoint.distanceToInitialEgo + self.vehicleLag)[0]

        # lastLoc = self.intermediatePoints[-2]
        # print(lastLoc, self.intermediatePoints[0])
        # lastLocWp = self.agent.map.get_waypoint(lastLoc)

        print("vehicleConflictWp", vehicleConflictWp)

        leftSideWalk, rightSidewalk = Utils.getSideWalks(self.agent.world, vehicleConflictWp)
        print(leftSideWalk, rightSidewalk)

        destination = leftSideWalk.location
        if self.navPath.direction == Direction.LR:
            destination = rightSidewalk.location
     

        self.intermediatePoints[-1] = destination
        self.setFinalDestination(destination)
        self.agent.setDestination(destination)
        # TODO some initial estimations may be wrong.


    # endregion

    # region simulation

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
        self.logger.info(f"has reached nav point {navPoint}")
        for behaviorType in navPoint.behaviorTags:
            # print(navPoint)
            self.logger.info(f"Tick {self.agent.currentEpisodeTick} : reached nav point {self.nextIntermediatePointIdx}. activating behavior {behaviorType}")
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


        if self.distanceToNextDestination() < 0.25: # 0.25 meters close
            self.activateBehaviorModels()
            return True
        
        destinationVec = nextDest - prevDest
        if destinationVec.length() < 0.1:
            print("destinationVec", destinationVec.length())
            print("prevDest", prevDest)
            print("nextDest", nextDest)
            print("nextIntermediatePointIdx", self.nextIntermediatePointIdx)
            print("next inter dest", len(self.intermediatePoints))
            print("intermediate points", self.intermediatePoints)
            print("nav points", self.navPath.path)
        destDirection = (nextDest - prevDest).make_unit_vector() # might be 0 if both nav points are at the same location
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
        
        force = requiredChangeInVelocity / 0.05 #instant change

        # if self.distanceToNextDestination() < 0.5:
        #     force = -1 * force

        return force
        
    
    def getAverageVelocityRequiredToReachNext(self) -> Optional[carla.Vector3D]:
        """Returns the average velocity required to reach the next intermediate point

        Returns:
            float: average velocity required to reach the next intermediate point
        """
        
        nextLoc = self.intermediatePoints[self.nextIntermediatePointIdx]

        if nextLoc == self.finalDestination:
            self.agent.logger.warning(f"no intermediate location. stopping nav path model")
            return None
        
        vehicle = self.agent.egoVehicle # this is not correct, we need the ego
        vehicleTravelD = self.vehicleDistanceToNavLocOnVehicleAxis(nextLoc, vehicle)


        if vehicleTravelD < 0:
            
            direction = (nextLoc - self.agent.location).make_unit_vector()
            self.logger.warn(f"vehicleTravelD is negative {vehicleTravelD}, Trying to reach next locatiton as fast as possible if the vehicle is still oncoming.")
            if InteractionUtils.isOncoming(self.agent.walker, vehicle):
                self.logger.warn(f"Fast forward to next")
                return 10 * direction # quickly move to the next dest
            return self.navPath.pedConfiguration.maxSpeed * direction
        
        # vehicle may stop
        vehicleSpeed = vehicle.get_velocity().length()
        if vehicleSpeed < 0.1:
            return None
        timeToReachNextNavPoint = vehicleTravelD / vehicleSpeed
        dToNext = self.agent.location.distance_2d(nextLoc)
        speed = dToNext / timeToReachNextNavPoint
        # print("vehicleTravelD", vehicleTravelD)
        # print("timeToReachNextNavPoint", timeToReachNextNavPoint)
        # print("nextLoc", nextLoc)
        # print("dToNext", dToNext)
        # print("speed", speed)
        direction = (nextLoc - self.agent.location).make_unit_vector()
        speed = max(speed, self.navPath.pedConfiguration.minSpeed)
        return speed * direction * 1.1
    
    # def getEgoTravelDistance(self) -> Optional[carla.Vector3D]:
    #     vehicle = self.agent.egoVehicle # this is not correct, we need the ego
        
    #     nextLoc = self.intermediatePoints[self.nextIntermediatePointIdx]
    #     nextNavPoint = self.navPath.path[self.nextIntermediatePointIdx]

    #     # debugLocation = carla.Location(x=vehicle.get_location().x, y=vehicle.get_location().y, z=vehicle.get_location().z + 1.0)
    #     # self.agent.visualizer.drawPoint(debugLocation, size=0.1, color=(255, 0, 0), life_time=10)

    #     vehicleWp: carla.Waypoint = self.agent.map.get_waypoint(vehicle.get_location())

    #     vehicleTravelD = self.vehicleDistanceToNavLocOnVehicleAxis(nextLoc, vehicle)
        

    #     locToVehicle = VehicleUtils.distanceToVehicle(nextLoc, vehicle, vehicleWp)
    #     print("locToVehicle before adjustment", locToVehicle)
    #     assert locToVehicle is not None

    #     if nextNavPoint.distanceToEgo < 0: # negative required distance
    #         # we need to make sure that when we reach this point, vehicle is past us
    #         if not self.isVehicleBehindNavLoc(nextLoc, vehicle): # tthis is not correct as we are checking against the agent's location. We need to check against the navpoint location.
    #             locToVehicle = -locToVehicle
    #     else: # positive required distance
    #         if not self.isVehicleBehindNavLoc(nextLoc, vehicle): # it really does not matter if the vehicle is oncoming or not.
    #             self.agent.logger.warning(f"vehicle is not oncoming for positive nav pointt. stopping nav path model")
    #             return None
            
    #     requiredDToVehicle = nextNavPoint.distanceToEgo
    #     vehicleTravelD = locToVehicle - requiredDToVehicle
    #     # print(vehicleTravelD)
    #     # raise Exception(f"stop here vehicleTravelD {vehicleTravelD}, requiredDToVehicle {requiredDToVehicle}, locToVehicle {locToVehicle}")
    #     print(f"stop here vehicleTravelD {vehicleTravelD}, requiredDToVehicle {requiredDToVehicle}, locToVehicle {locToVehicle}")
    #     print(f"current nav index {self.nextIntermediatePointIdx}")
    
    #     return vehicleTravelD
    
    

    def vehicleDistanceToNavLocOnVehicleAxis(self, navLoc: carla.Location, vehicle: carla.Vehicle) -> float:
        """Distance is positive when vehicle's distance is greater than distanceToEgo and vehicle is moving towards the distanceToEgo. 
        
        It's a complicated method as distanceToEgo can be positive or negative. Basically it will return a negative distance if vehicle overshoots.

        Args:
            navLoc (carla.Location): _description_
            vehicle (carla.Vehicle): _description_

        Returns:
            float: _description_
        """
        navPoint = self.intermediatePointsToNavPointMap[navLoc]
        # to measure the distance, we need a projection vehicle's nearest location
        # vehicleLocation = VehicleUtils.getNearestLocationOnVehicleAxis(navLoc, vehicle, vehicleWp)
        V_Ref = self.getVehicleReferenceLocation(navPoint, vehicle)
        V_Z_Wp= self.getVehicleWpAtDistanceToEgo(navPoint.distanceToEgo, V_Ref)
        

        Z = V_Z_Wp.transform.location # relative goal point wrt current vehicle position. We need to move Z to G
        # G = Utils.projectAonB2D(navLoc, Z)
        # V_G = G - V_Ref
        V_N = navLoc - V_Ref # the vector from the current reference location to the actual nav location
        V_Z = Z - V_Ref # the vector from current reference location to the point at distanceToEgo on the vehicle axis
        V_G = Utils.projectAonB2D(V_N, V_Z)
        G = V_Ref + V_G 
        V_ZG = G - Z

        # this assertions make it safe
        d1 = Z.distance_2d(V_Ref)
        # print("V_Ref", V_Ref)
        # print("Z", Z)
        # print("navPoint.distanceToEgo", navPoint.distanceToEgo)
        # print("d1", d1)
        assert d1 < abs(navPoint.distanceToEgo) * 1.1 + 1.5 # during the lane change, d1 can grow quite large as Z can be on the old lane and vehicle ref is moving out of the lane.
        assert d1 > abs(navPoint.distanceToEgo) * 0.9 # when the vehicle rotates it can shrink less than the width!
        # overkill assertions can be turned off

        debugLocation = carla.Location(x=Z.x, y=Z.y, z = 0.5) # WP location is V_Z's location in world coordinates
        self.agent.visualizer.drawPoint(debugLocation, size=0.1, color=(0, 255, 0), life_time=10)

        distanceToTravel = V_ZG.length()
        # Check overshoot
        if navPoint.distanceToEgo < 0 and V_G.dot(V_Z) > 0:
            distanceToTravel = - distanceToTravel
        elif navPoint.distanceToEgo > 0 and V_G.dot(V_Z) < 0:
            distanceToTravel = - distanceToTravel

        if distanceToTravel < 0:
            self.agent.logger.info(f"vehicle has already crossed the nav point. distanceToTravel {distanceToTravel}, navPoint.distanceToEgo {navPoint.distanceToEgo}")

            self.agent.logger.debug("navPoint.distanceToEgo", navPoint.distanceToEgo)
            self.agent.logger.debug("vehicleLocation", vehicle.get_location())
            self.agent.logger.debug("V_Ref:", V_Ref)
            self.agent.logger.debug("V_Z", V_Z)
            self.agent.logger.debug("V_N:", V_N)
            self.agent.logger.debug("V_G", V_G)
            self.agent.logger.debug("Z", Z)
            self.agent.logger.debug("N:", navLoc)
            self.agent.logger.debug("G", G)
            self.agent.logger.debug("V_ZG", V_ZG)
            self.agent.logger.debug("V_ZG.length", V_ZG.length())

        return distanceToTravel

    
    def getVehicleReferenceLocation(self, navPoint: NavPoint, vehicle: carla.Vehicle) -> carla.Location:
        if navPoint.distanceToEgo < 0:
            vehicleRefLocation = VehicleUtils.getVehicleBackLocation(vehicle)
        else:
            vehicleRefLocation = VehicleUtils.getVehicleFrontLocation(vehicle)
        return vehicleRefLocation
    
    def getVehicleWpAtDistanceToEgo(self, distanceToEgo: float, vehicleRefLocation: carla.Location) -> carla.Waypoint:
        """Based on the current vehicleRefLocation, it returns the waypoint of the vehicle at navPoint.distanceToEgo

        Args:
            distanceToEgo (float): distanceToEgo of the NavPoint
            vehicleRefLocation (carla.Location): _description_

        Returns:
            carla.Waypoint: _description_
        """
        refWp: carla.Waypoint = self.agent.map.get_waypoint(vehicleRefLocation)
        if distanceToEgo < 0:
            return refWp.previous(-distanceToEgo)[0] 
        else:
            return refWp.next(distanceToEgo)[0]
        

    
    #endregion