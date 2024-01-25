import math
from random import random
from agents.pedestrians.factors.InternalFactors import InternalFactors
import numpy as np
import time
import carla
import logging
from agents.pedestrians.BehaviorType import BehaviorType

from agents.pedestrians.soft.NavPath import NavPath
from .InfoAgent import InfoAgent
from lib import SimulationVisualization
from .planner.PedestrianPlanner import PedestrianPlanner
from .PedState import PedState
from .StateTransitionManager import StateTransitionManager
from typing import Dict, List, Optional, Set
from .PedUtils import PedUtils
from lib import Geometry, Utils


class PedestrianAgent(InfoAgent):
    
    def __init__(self, walker, time_delta, visualizer=None, config=None):
        """
        Initialization the agent paramters, the local and the global planner.

            :param walker: actor to apply to agent logic onto
            :param desired_speed: speed (in m/s) at which the vehicle will move range is (0.7-5.7) Pedestrian acceleration and speeds, 2012
            :param opt_dict: dictionary in case some of its parameters want to be changed.
                This also applies to parameters related to the LocalPlanner.
        """

        self.name = f"PedestrianAgent #{walker.id}"
        self.state = PedState.INITALIZING
        super().__init__(self.name, walker, config=config)
        self._world = self._walker.get_world()
        self._map = self._world.get_map()

        self.skip_ticks = 20 # takes about 10 ticks for the vehicle to start
        self.time_delta = time_delta
        self.tickCounter = 0

        self.visualizer = visualizer


        self._last_jumped = time.time_ns()

        self.collisionSensor = None
        self.obstacleDetector = None

        self.visualizationForceLocation = None
        if config is not None:
            if "visualizationForceLocation" in config:
                self.visualizationForceLocation = config["visualizationForceLocation"]

        self.visualizationInfoLocation = None
        if config is not None:
            if "visualizationInfoLocation" in config:
                self.visualizationInfoLocation = config["visualizationInfoLocation"]

        
                
        # config parameters
        self.navPath: NavPath = None
        self.currentBehaviors: Set[BehaviorType] = set([])
        # self.dynamicBehaviorModelFactory = None

    @property
    def world(self):
        return self._world

    @property
    def map(self):
        return self._map

    @property
    def actorManager(self):
        return self._localPlanner.actorManager
    @property
    def obstacleManager(self):
        return self._localPlanner.obstacleManager
    
    @property
    def internalFactors(self) -> InternalFactors:
        return self._localPlanner.internalFactors
    
    @property
    def egoVehicle(self) -> carla.Vehicle:
        return self.actorManager.egoVehicle
    
    def setEgoVehicle(self, vehicle: carla.Vehicle):
        self.actorManager.setEgoVehicle(vehicle)

    
    def setNavPath(self, navPath: NavPath, startFromSidewalk:bool = True, endInSidewalk: bool=True, vehicleLagForInitialization: float = 10):
        self.navPath = navPath
        self._localPlanner.getDestinationModel().addNavPathModel(
            self.navPath, 
            startFromSidewalk=startFromSidewalk, 
            endInSidewalk=endInSidewalk, 
            vehicleLagForInitialization=vehicleLagForInitialization
            )
  
    def getAvailableTimeGapWithClosestVehicle(self):
        # time gap = time taken for the oncoming vehicle to reach + time to cross the lane.
        # TODO assuming vehicle driving in agent's nearest lane 
        # TODO Assuming pedestrian will cross at desired speed.
        TTC = self.actorManager.pedPredictedTTCNearestOncomingVehicle()
        TG = self.actorManager.pedTGNearestOncomingVehicle()
        
        self.logger.info(f"predicted TTC = {TTC} seconds")
        self.logger.info(f"absolute TG (ignoring conflict point) = {TG} seconds")

        if TG is None: # Vehicle already crossed
            return None



        TG = self._addErrorToTimeEstimtion(TG)

        self.logger.info(f"Perceived TG (Time gap) = {TG} seconds")

        return TG
    
    def getAvailableTimeGapWithEgo(self):
        # time gap = time taken for the oncoming vehicle to reach + time to cross the lane.
        # TODO assuming vehicle driving in agent's nearest lane 
        # TODO Assuming pedestrian will cross at desired speed.
        # TTC = self.actorManager.pedPredictedTTCNearestEgo()
        TG = self.actorManager.pedTGNearestEgo()
        
        # self.logger.info(f"Ego predicted TTC = {TTC} seconds")
        self.logger.info(f"Ego absolute TG (ignoring conflict point) = {TG} seconds")

        if TG is None: # Vehicle already crossed
            return None



        TG = self._addErrorToTimeEstimtion(TG)

        self.logger.info(f"EGO Perceived TG (Time gap) = {TG} seconds")

        return TG
    

    def ttcWithEgo(self):
        return self.actorManager.pedPredictedTTCNearestEgo()
    
    def distanceFromEgo(self):
        return self.actorManager.distanceFromEgo()


    def _addErrorToTimeEstimtion(self, T):
        # TODO better modeling than a noise, error = f(distance, speed, occlusions, etc)"
        # noiseFactor = np.random.uniform(0.8, 1.2) NOISE CANNOT BE RANDOM
        noiseFactor = self._localPlanner.getInternalFactor("TG_multiplier")

        return T * noiseFactor # TODO error modeling in Gap

    
    def getPredictedConflictPoint(self):
        return self._localPlanner.getPredictedConflictPoint()

    #region states

    def isCrossing(self):
        if self.state == PedState.CROSSING:
            return True
        return False

    def isWaiting(self):
        if self.state == PedState.WAITING:
            return True
        return False

    def isFrozen(self):
        if self.state == PedState.FROZEN:
            return True
        return False

    def isFinished(self):
        if self.state == PedState.FINISHED:
            return True
        return False

    def isSurviving(self):
        if self.state == PedState.SURVIVAL:
            return True
        return False

    def isMovingTowardsDestination(self):
        return self._localPlanner.isMovingTowardsDestination()

    #endregion 
    
    # region visualization
    def visualiseState(self):
        self.visualizer.drawPedState(self.state, self.walker, life_time=0.1)


    def visualizeConflictPoint(self):
        conflictPoint = self._localPlanner.getPredictedConflictPoint()
        if conflictPoint is None:
            return
        conflictPointLocation = carla.Location(x=conflictPoint.x, y=conflictPoint.y, z=1.0)

        self.visualizer.drawPoint(conflictPointLocation, size=0.2, color=(100, 0, 0), life_time = 0.1)

    

    def visualiseForces(self):
        forces = self._localPlanner.modelForces

        visualizationForceLocation = self.location + carla.Location(x=10)
        if self.visualizationForceLocation is not None:
            visualizationForceLocation = self.visualizationForceLocation

        visualizationInfoLocation = self.location + carla.Location(x=10)
        if self.visualizationInfoLocation is not None:
            visualizationInfoLocation = self.visualizationInfoLocation
            
        self.visualizer.visualizeForces(
            self.name, 
            forces = forces, 
            forceCenter = visualizationForceLocation, 
            infoCenter = visualizationInfoLocation, 
            life_time=0.1
            )
    #endregion
    

    def isInitializing(self): 
        if self.skip_ticks == 0:
            return False

        self.tickCounter += 1
        if self.tickCounter == self.skip_ticks:
            # time to wait
            StateTransitionManager.changeAgentState(f"{self.name}.isInitializing", self, PedState.WAITING)

        if self.tickCounter >= self.skip_ticks:
            return False

        return True

    def reset(self, newStartPoint:carla.Location=None):
        self.logger.info(f"Resetting")
        super().reset()
        
        self._localPlanner.reset()

        if newStartPoint is not None:
            self._walker.set_location(newStartPoint)

        self.tickCounter = 0
        StateTransitionManager.changeAgentState(f"{self.name}.isInitializing", self, PedState.INITALIZING)
        pass


    def printLocations(self):
        print("Agent location", self._walker.get_location())
        print("Collision location", self.collisionSensor.get_location())
        print("Obstacle detector location", self.obstacleDetector.get_location())

    def getStopControl(self):
        return self._localPlanner.getStopControl()

    def calculateControl(self):
        if self.destination is None:
            raise Exception("Destination is none")

        if self.debug:
            self.visualiseState()

        
        if  self.isInitializing():
            if self.debug:
                self.logger.info(f"Pedestrian is {self.state}.")
                self.visualiseState()
            return self.getStopControl()

        # if self.isFinished():
        #     self.visualiseState()
        
 
        location = self.feetLocation
        # speed = self.calculateNextSpeed(direction)


        if self.climbSidewalkIfNeeded():
            # return a stop control
            return self._localPlanner.getSidewalkClimbedControl()

        control = self._localPlanner.calculateNextControl()

        direction = control.direction
        self.visualizer.drawDirection(location, direction, life_time=0.1)

        if self.debug:
            self.visualizeConflictPoint()
            self.visualiseState()
            self.visualiseForces()
        
        self.visualiseForces()
        self.visualiseState()

        return control


    # def calculateNextSpeed(self, direction):

    #     # TODO make a smooth transition
    #     # oldControl = self._walker.get_control()
    #     # currentSpeed = oldControl.speed
    #     # nextSpeed = max()
    #     return self.desired_speed



    #region sidewalk

    def canClimbSideWalk(self):

        if self.isFinished():
            return False

        if self.timeSinceLastJumpMS() < 1000:
            return False
        
        if self.onSideWalk():
            return False

        distance = self.getDistanceToSidewalkAhead(rayLength=1) 
        if distance is None:
            self.logger.info(f"Distance to sidewalk is none!")

            return False

        self.logger.debug(f"current distance to sidewalk is {distance}")
        distance -= self.getOldSpeed() * self.time_delta
        self.logger.debug(f"after tick distance to sidewalk is {distance}")

        # walkerSpeed = self.getOldSpeed()

        # if distance < walkerSpeed * 2 and distance > walkerSpeed:
        # if distance < 0.2 and distance > 0.1:
        if distance < 0.7:
            self.logger.debug(f"after tick distance to sidewalk is {distance}. Can jump")
            return True
        return False

    def updateJumped(self):
        self._last_jumped = time.time_ns()

    def timeSinceLastJumpMS(self):
        diff = (time.time_ns() - self._last_jumped) // 1_000_000 
        return diff

    def climbSidewalkIfNeeded(self):

        location = self.location

        if self.canClimbSideWalk():
            self.updateJumped()
            # print((f"{self.name} climbing up a sidewalk."))
            self.logger.warn(f"{self.name} climbing up a sidewalk.")
            # self._walker.add_force(carla.Vector3D(0, 0, 10))
            # velocity = self.getOldVelocity() # sometimes old velocity is too low due to collision with the sidewalk..
            
            # velocity = self.speedToVelocity(self.desired_speed)
            velocity = self.speedToVelocity(2.0)

            # self._walker.set_location(
            #     carla.Location(
            #         location.x + velocity.x * self.time_delta * 5,
            #         location.y + velocity.y * self.time_delta * 5,
            #         location.z + 0.5
            # ))

            # issue with velocity is when it's close to 0 nothing works.
            
            # desiredDirection = self._localPlanner.desiredDirection
            
            StateTransitionManager.changeAgentState(self.name, self, PedState.CLIMBING_SIDEWALK)

            sidewalkDirection = self.getDirectionToSidewalkAhead()

            translation = sidewalkDirection * 1.5

            self._walker.set_location(
                carla.Location(
                    location.x + translation.x,
                    location.y + translation.y,
                    location.z + 0.5
            ))
            return True
        return False
    

    def onSideWalk(self) -> bool:
        # cast a vertical direction ray
        actorLocation = self._walker.get_location()
        destinationXYLocation = carla.Location(x = actorLocation.x, y = actorLocation.y, z=-1)
        labeledObjects = self._world.cast_ray(actorLocation, destinationXYLocation)
        # for lb in labeledObjects:
        #     print(f"Labeled point location {lb.location} and semantic {lb.label} distance {actorLocation.distance(lb.location)}")
        
        for lb in labeledObjects:
            if lb.label == carla.CityObjectLabel.Sidewalks:
                return True
        return False


    def getDistanceToSidewalkAhead(self, rayLength=3) -> Optional[float]:
        sidewalk = self.getSidewalkAhead(rayLength=rayLength)
        if sidewalk is None:
            return None
        
        actorLocation = self._walker.get_location()
        distance = actorLocation.distance_2d(sidewalk.location)
        self.logger.info(f"Sidewalk location {sidewalk.location} and semantic {sidewalk.label} XY distance {distance}")
        return distance
    
    def getDirectionToSidewalkAhead(self, rayLength=3) -> Optional[carla.Vector3D]:
        sidewalk = self.getSidewalkAhead(rayLength=rayLength)
        if sidewalk is None:
            return None
        
        actorLocation = self._walker.get_location()
        return (sidewalk.location - actorLocation).make_unit_vector()


    def getSidewalkAhead(self, rayLength=3) -> Optional[carla.LabelledPoint]:
        actorLocation = self._walker.get_location()
        actorXYLocation = carla.Location(x = actorLocation.x, y = actorLocation.y, z=0.05)
        actorVelocity = self.getOldVelocity()
        actorSpeed = actorVelocity.length()
        if actorSpeed == 0:
            return None
                # based on forward vector of the old contorl
        oldControl = self.getOldControl()
        forwardVector = oldControl.direction * rayLength
        destinationXYLocation = carla.Location(x = actorLocation.x + forwardVector.x, y = actorLocation.y + forwardVector.y, z=0.05)
        labeledObjects = self._world.cast_ray(actorXYLocation, destinationXYLocation)
        # print(labeledObjects)
        for lb in labeledObjects:
            if lb.label == carla.CityObjectLabel.Sidewalks:
                return lb

        return None

    # def getObstaclesToDestination(self):
    #     actorLocation = self._walker.get_location()
    #     actorXYLocation = carla.Location(x = actorLocation.x, y = actorLocation.y, z=0.05)
    #     destinationXYLocation = carla.Location(x = self.destination.x, y = self.destination.y, z=0.05)
    #     labeledObjects = self._world.cast_ray(actorXYLocation, destinationXYLocation)
    #     # for lb in labeledObjects:
    #     #     print(f"Labeled point location {lb.location} and semantic {lb.label} distance {actorLocation.distance(lb.location)}")
    #     return labeledObjects
    
    # def distanceToNextSideWalk(self):
    #     actorLocation = self._walker.get_location()
    #     # actorXYLocation = carla.Location(x = actorLocation.x, y = actorLocation.y, z=0.)
    #     labeledObjects = self.getObstaclesToDestination()
    #     for lb in labeledObjects:
    #         if lb.label == carla.CityObjectLabel.Sidewalks:
    #             # if self.visualizer is not None and self.debug:
    #             #     self.visualizer.drawPoint(carla.Location(lb.location.x, lb.location.y, 1.0), color=(0, 0, 255), life_time=1.0)
    #             # sidewalkXYLocation = carla.Location(x = lb.location.x, y = lb.location.y, z=0.)
    #             # distance = actorXYLocation.distance_2d(sidewalkXYLocation)
    #             distance = actorLocation.distance_2d(lb.location)
    #             self.logger.info(f"Sidewalk location {lb.location} and semantic {lb.label} XY distance {distance}")
    #             return distance
    #     return None

    
    def hasReachedDestinationAlongLocalY(self, destination: carla.Location, tolerance: float):
        

        desVector = destination - self.location
        desVector.z = 0

        # print("destination", destination)
        # print("distance to next destination", desVector.length())

        if desVector.length() < tolerance:
            return True
        
        # overshoot check. If destination vector is in the opposite direction of the local Y direction, then we have overshooted. This is causing problems.
        if abs(Utils.angleBetweenVectors(desVector, self.localYDirection)) > math.pi / 2:
            return True
        return False



    #endregion
    #region sensor handlers

    def handleWalkerCollision(self, data):
        if self.isSidewalk(data.other_actor):
            self.logger.info(f"{self.name} hits a sidewalk")
        else:
            self.logger.info(f"{self.name} hits a non-sidewalk")


    def handWalkerObstacles(self, data):
        # self.logger.info(f"{self.name} sees a obstackle {data.distance}m away with semantic tag {data.other_actor.semantic_tags}")
        # self.logger.info("semantic tag", data.other_actor.semantic_tags)
        # if self.isSidewalk(data.other_actor):

        #     if data.distance < 0.1:
        #         self.logger.info(f"{self.name} is on a sidewalk {data.distance}m away")
        #     else:
        #         self.logger.info(f"{self.name} sees a obstackle {data.distance}m away")

        #     # self._needJump = True
        return
    
    def isSidewalk(self, actor):
        if 8 in actor.semantic_tags:
            return True
        return False

    #endregion



    