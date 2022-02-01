
import carla
from typing import Dict, List
from lib.LoggerFactory import LoggerFactory


class ActorManager:

    """
    Each actor has their own instance of ActorManager
    """

    def __init__(self, actor: carla.Actor):
        
        self.name = f"ActorManager #{actor.id}"
        self.logger = LoggerFactory.create(self.name)

        self._actor = actor
        self._world = actor.get_world()
        self._map = self.world.get_map()
        self._cache = {}
        self._currentActorDistances = {}
        self._previousActorDistances = {}

    @property
    def actor(self):
        return self._actor

    @property
    def map(self):
        return self._map

    @property
    def world(self):
        return self._world


    @property
    def actorList(self):
        return self.world.get_actors()
        
    def isSidewalk(self, actor):
        if 8 in actor.semantic_tags:
            return True
        return False

    def getActorTypes(self):
        types = set()
        for actor in self.actorList:
            types.add(actor.type_id)
        return types
    
    def onTick(self, world_snapshot):
        # # cache results of all the function calls every tick.
        actorLocation = self.actor.get_location()

        # self.logger.warn(f"previous distances before update {self._previousActorDistances}")
        # self.logger.warn(f"current distances before update {self._currentActorDistances}")

        self._previousActorDistances = self._currentActorDistances
        self._currentActorDistances = {} # new dict
        for otherActor in self.getDynamicActors():
            if self.actor.id == otherActor.id:
                continue
            self._currentActorDistances[otherActor.id] = actorLocation.distance_2d(otherActor.get_location())
        
        self.logger.debug(f"previous distances {self._previousActorDistances}")
        self.logger.debug(f"current distances {self._currentActorDistances}")
        pass
        # raise Exception("Not implemented yet")

    def getCurrentDistance(self, otherActor):
        return self._currentActorDistances[otherActor.id]

    def getPreviousDistance(self, otherActor):
        return self._previousActorDistances[otherActor.id]

    # region Oncoming
    def isOncoming(self, otherActor):

        self.logger.debug(f"actor previous distance {self._previousActorDistances[otherActor.id]} and current distance {self._currentActorDistances[otherActor.id]}")
        if otherActor.id not in self._previousActorDistances:
            self.logger.debug(f"actor not oncoming as previous distance is unknown")
            return False # in the first tick there will not be any previous distance
        if self._previousActorDistances[otherActor.id] > self._currentActorDistances[otherActor.id]: # TODO improve this algorithm
            # self.logger.info(f"actor oncoming")
            return True

        # self.logger.info(f"actor not oncoming")
        return False
    
    def getOncomingVehicles(self):
        oncomingVs = []
        for vehicle in self.getVehicles():
            if self.isOncoming(vehicle):
                oncomingVs.append(vehicle)
        self.logger.warn("Oncoming vehicles", oncomingVs)
        return oncomingVs
    
    def getNearestOnComingVehicle(self):
        oncomingVs = self.getOncomingVehicles()
        minD = 999999
        minVehicle = None
        for vehicle in oncomingVs:
            currentDistance = self.getCurrentDistance(vehicle)
            if currentDistance < minD:
                minD = currentDistance
                minVehicle = vehicle
        return minVehicle

    #endregion
    def getDynamicActors(self) -> List[carla.Actor]:
        das = []
        for actor in self.getVehicles():
            das.append(actor)
        for actor in self.getPedestrians():
            das.append(actor)
        return das

    def getStaticActors(self):
        sas = []
        for actor in self.getTrafficLights():
            sas.append(actor)
        for actor in self.getTrafficSigns():
            sas.append(actor)
        return sas


    def getVehicles(self) -> carla.ActorList:
        return self.actorList.filter('vehicle.*')

    def getPedestrians(self) -> carla.ActorList:
        return self.actorList.filter('walker.pedestrian.*')

    def getTrafficLights(self) -> carla.ActorList:
        return self.actorList.filter("*traffic_light*")

    def getTrafficSigns(self) -> carla.ActorList:
        return self.getTrafficStopSigns() + self.getTrafficYieldSigns()

    def getTrafficStopSigns(self) -> carla.ActorList:
        return self.actorList.filter("traffic.stop") 

    def getTrafficYieldSigns(self) -> carla.ActorList:
        return self.actorList.filter("traffic.yield") 

    def getTrafficSpeedSigns(self) -> carla.ActorList:
        return self.actorList.filter("traffic.speed") 
