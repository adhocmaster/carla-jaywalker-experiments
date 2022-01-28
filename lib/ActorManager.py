
import carla
from typing import Dict


class ActorManager:

    def __init__(self, actor: carla.Actor):
        
        self._actor = actor
        self._world = actor.get_world()
        self._map = self.world.get_map()
        self._cache = {}

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
        # cache results of all the function calls every tick.
        raise Exception("Not implemented yet")


    def getDynamicActors(self):
        return self.getVehicles() + self.getPedestrians()

    def getStaticActors(self):
        return self.getTrafficLights() + self.getTrafficSigns()

    def getVehicles(self):
        return self.actorList.filter('vehicle.*')

    def getPedestrians(self):
        return self.actorList.filter('walker.pedestrian.*')

    def getTrafficLights(self):
        return self.actorList.filter("*traffic_light*")

    def getTrafficSigns(self):
        return self.getTrafficStopSigns() + self.getTrafficYieldSigns()

    def getTrafficStopSigns(self):
        return self.actorList.filter("traffic.stop") 

    def getTrafficYieldSigns(self):
        return self.actorList.filter("traffic.yield") 

    def getTrafficSpeedSigns(self):
        return self.actorList.filter("traffic.speed") 
