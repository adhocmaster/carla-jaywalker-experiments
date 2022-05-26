import carla
from collections import deque
from abc import abstractmethod
from agents.pedestrians.ForceModel import ForceModel
from agents.pedestrians.StateTransitionModel import StateTransitionModel
from lib import ActorManager, ObstacleManager, Utils, NotImplementedInterface, InvalidParameter
from agents.pedestrians.factors import InternalFactors
from agents.pedestrians.factors.CrossingFactorModel import CrossingFactorModel
from agents.pedestrians.survival_models.SurvivalModel import SurvivalModel
from typing import List, Dict
import numpy as np

class PedestrianPlanner:
    """A planner has the state of the world, state of the pedestrian, and factors of the pedestrian. It does not plan any path or trajectory. 
    It's whole job is to send required states to factor models, get the force and state of the pedestrian. Apply the force and state in the world.
    """

    def __init__(self, agent, actorManager: ActorManager, obstacleManager: ObstacleManager,
                    internalFactors: InternalFactors, time_delta) -> None:
        self._agent = agent
        self._world = agent.walker.get_world()
        self.time_delta = time_delta
        
        self._map = self.world.get_map()
        self.actorManager = actorManager
        self.obstacleManager = obstacleManager
        self._destination = None
        self.internalFactors = internalFactors

        self.models: List[ForceModel] = []
        self.stateTransitionModels: List[StateTransitionModel] = []
        self.crossingFactorModels: List[CrossingFactorModel] = []
        self.survivalModels: List[SurvivalModel] = []
        self.freezingModels: List[SurvivalModel] = []

        self.modelCoeff: Dict[str, float] = {}

        self.modelForces: Dict[str, carla.Vector3D] = {} # tracks the forces for the next tick

        # we will save 2 seconds of previous locations.
        deqLength = max(1, int(2 / self.time_delta))
        self.logger.warn(f"remembering {deqLength} tick locations")
        self.locations: List[carla.Location] = deque(maxlen=deqLength) # list of previous locations of this agent.



        pass

    @property
    def agent(self):
        return self._agent

    @property
    def world(self):
        return self._world

    @property
    def map(self):
        return self._map

    @property
    @abstractmethod
    def logger(self):
        pass

    def getInternalFactor(self, name):
        return self.internalFactors[name] 

    def setInternalFactor(self, name, val):
        self.internalFactors[name] = val

    @property
    def desiredSpeed(self):
        return self.internalFactors["desired_speed"] 

    @property
    def desiredDirection(self):
        return self.getDestinationModel().getDesiredDirection()

    @property
    def maxSpeed(self):
        return self.internalFactors["max_crossing_speed"]

    @property
    def minSpeed(self):
        return self.internalFactors["min_crossing_speed"]

    @property
    def maxAcceleration(self):
        return self.internalFactors["acceleration_positive_max"]


    @property
    def minAcceleration(self):
        return self.internalFactors["acceleration_negative_min"]
    
    @property
    def destination(self):
        return self._destination


    def reset(self):
        for name in self.modelCoeff:
            self.modelCoeff[name] = 1.0
        
    def updateModelCoeff(self, name, val):
        self.modelCoeff[name] = val
        
    def isMovingTowardsDestination(self):

        """Based on the angle between the desired direction and current direction
        """

        #TODO
        currentVelocity = self.agent.velocity

        if currentVelocity.length() <0.001:
            return True
        
        currentDirection = currentVelocity.make_unit_vector()
        desiredDirection = self.desiredDirection

        angle = abs(Utils.angleBetweenDirections(currentDirection, desiredDirection))
        if angle > (np.pi / 2):
            return False
        
        return True



    def onTickStart(self, world_snapshot):
        self.locations.append(self.agent.location)
        self.actorManager.onTickStart(world_snapshot)
        self.obstacleManager.onTickStart(world_snapshot)
        self.setFactorModelDestinationParams()

    def setDestination(self, destination):
        self._destination = destination
        self.getDestinationModel().setFinalDestination(destination)

    
    def done(self):
        if self.getDistanceToDestination() < 0.2:
            self.logger.warn(f"Reached destination {self.getDistanceToDestination()}")
            return True
        else:
            self.logger.info(f"Distance to destination {self.getDistanceToDestination()}")
        return False
            
    def getDistanceToDestination(self):
        return Utils.getDistance(self.agent.feetLocation, self._destination, ignoreZ=True)

    def getDesiredDirection(self):
        return Utils.getDirection(self.agent.feetLocation, self._destination, ignoreZ=True)

    def getStopControl(self):
        oldControl = self.agent.getOldControl()
        
        control = carla.WalkerControl(
            direction = oldControl.direction,
            speed = 0,
            jump = False
        )
        return control

    def getSidewalkClimbedControl(self):
        oldControl = self.agent.getOldControl()
        
        control = carla.WalkerControl(
            direction = oldControl.direction,
            speed = 0.5,
            jump = False
        )
        return control

    def getNewControl(self):
        """Calculates new control by multiplying the resultant force by time delta
        """
        newVelocity = self.getNewVelocity()
        speed = newVelocity.length()
        if speed > 0:
            direction = newVelocity.make_unit_vector()
            return carla.WalkerControl(
                    direction = direction,
                    speed = speed,
                    jump = False
                )
        else:
            return self.getStopControl()

    def getNewVelocity(self):
        oldVelocity = self.agent.getOldVelocity()
        dv = self.getRequiredChangeInVelocity()
        newVelo = oldVelocity + dv
        

        # we have two constraints
        # 1. speed cannot go beyond maximum speed.
        # 2. acceleration cannot go beyond max accelration. # which is clipped on resultant force.
        # we just have to check the #1
        if newVelo.length() > 0:
            newDirection = newVelo.make_unit_vector()
            newSpeed = min(self.maxSpeed, newVelo.length())

            newVelo = newDirection * newSpeed

        self.logger.info(f"Speed {oldVelocity.length()} -> {newVelo.length()}")

        return newVelo

    def getRequiredChangeInVelocity(self):
        timeDelta = Utils.getTimeDelta(self.world)
        if timeDelta < 0.001:
            raise InvalidParameter("Time delta too low for Pedestrian Planner")

        force = self.getResultantForce() # unit mass, so force == acceleration
        self.logger.info(f"Resultant force is {force}")
        self.logger.info(f"Resultant acceleration is {force.length()} m/s^2")
        self.logger.info(f"timeDelta is {timeDelta}")
        dv = force * timeDelta
        return dv

    
    def getResultantForce(self):

        resultantForce = carla.Vector3D()

        for model in self.models:
            force = model.calculateForce()
            self.logger.info(f"Force from {model.name} {force}")
            self.modelForces[model.name] = force
            
            if force is not None:
                resultantForce += force
        
        # clip force
        if resultantForce.length() > self.maxAcceleration:
            self.logger.info(f"Clipping {resultantForce.length()} to {self.maxAcceleration}")
            resultantForce = resultantForce.make_unit_vector() *  self.maxAcceleration

        # clip force
        if resultantForce.length() < self.minAcceleration:
            self.logger.info(f"Clipping {resultantForce.length()} to {self.minAcceleration}")
            resultantForce = resultantForce.make_unit_vector() *  self.minAcceleration

        return resultantForce

    def setFactorModelDestinationParams(self):
        """Must be run every tick
        """
        destinationModel = self.getDestinationModel()

        destForce = destinationModel.calculateForce()
        destVelocity = destinationModel.getDesiredVelocity()
        destDirection = destinationModel.getDesiredDirection()
        destSpeed = destVelocity.length()

        for crossingFactorModel in self.crossingFactorModels:
            crossingFactorModel.setDestinationParams(destForce, destDirection, destSpeed)
        
        pass

    

    def getPredictedConflictPoint(self):
        """ TODO Will not work correctly for multiple"""
        if self.actorManager.nearestOncomingVehicle is None:
            return None

        # if current speed is almost 0, get desired direction from destination model
        if self.agent.velocity.length() < 0.01:
            return self.getPredictedConflictPointTowardsDestination()
        else:
            velocity =  self.agent.direction * self.desiredSpeed
        
        return self.actorManager.getPredictedConflictPoint(self.actorManager.nearestOncomingVehicle, velocity)

    
    def getPredictedConflictPointTowardsDestination(self):
        
        velocity = self.getDestinationModel().getDesiredVelocity()
        return self.actorManager.getPredictedConflictPoint(self.actorManager.nearestOncomingVehicle, velocity)


    @abstractmethod
    def getDestinationModel(self) -> ForceModel:
        raise NotImplementedInterface("getDestinationModel")



    @abstractmethod
    def calculateNextPedestrianState(self):
        raise NotImplementedInterface("calculateNextPedestrianState")

    @abstractmethod
    def calculateNextPedestrianState(self):
        raise NotImplementedInterface("calculateNextPedestrianState")

    @abstractmethod
    def calculateNextControl(self):
        raise NotImplementedInterface("calculateNextControl")

    @abstractmethod
    def calculateResultantForce(self):
        raise NotImplementedInterface("calculateResultantForce")

    @abstractmethod
    def getOncomingVehicles(self):
        raise NotImplementedInterface("getOncomingVehicles")

    @abstractmethod
    def getOncomingPedestrians(self):
        raise NotImplementedInterface("getOncomingPedestrians")

        
    @abstractmethod
    def getPrecedingPedestrians(self):
        raise NotImplementedInterface("getPrecedingPedestrians")

    @abstractmethod
    def getFollowingPedestrians(self):
        raise NotImplementedInterface("getFollowingPedestrians")