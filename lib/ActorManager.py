
import carla
import math
from typing import Dict, List
from lib.LoggerFactory import LoggerFactory
from lib.utils import Utils


class ActorManager:

    """
    Each actor has their own instance of ActorManager
    """

    def __init__(self, actor: carla.Actor, time_delta):
        
        self.name = f"ActorManager #{actor.id}"
        self.logger = LoggerFactory.create(self.name)
        self.time_delta = time_delta

        self._actor = actor
        self._world = actor.get_world()
        self._map = self.world.get_map()
        self._tickCache = {}
        self._currentActorDistances = {} # for vehicles, the distance is calculated from the nearest waypoint for an actor.
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
    def nearestOncomingVehicle(self):
        return self.calculateNearestOnComingVehicle()


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
    
    def onTickStart(self, world_snapshot):
        self._tickCache = {} # clear cache.
        # # cache results of all the function calls every tick.
        actorLocation = self.actor.get_location()

        # get nearest waypoint
        wp = self.map.get_waypoint(actorLocation)
        wpLocation = wp.transform.location

        # self.logger.warn(f"previous distances before update {self._previousActorDistances}")
        # self.logger.warn(f"current distances before update {self._currentActorDistances}")

        self._previousActorDistances = self._currentActorDistances
        self._currentActorDistances = {} # new dict
        for otherActor in self.getDynamicActors():
            if self.actor.id == otherActor.id:
                continue
            self._currentActorDistances[otherActor.id] = wpLocation.distance_2d(otherActor.get_location()) - Utils.getMaxExtent(otherActor)
            # self._currentActorDistances[otherActor.id] = actorLocation.distance_2d(otherActor.get_location())
        
        self.logger.info(f"previous distances {self._previousActorDistances}")
        self.logger.info(f"current distances {self._currentActorDistances}")

        self.calculateNearestOnComingVehicle()
        pass
        # raise Exception("Not implemented yet")

    def getCurrentDistance(self, otherActor):
        return self._currentActorDistances[otherActor.id]

    def getPreviousDistance(self, otherActor):
        return self._previousActorDistances[otherActor.id]

    # region Oncoming
    def isOncoming(self, otherActor):

        if otherActor.id not in self._previousActorDistances:
            self.logger.debug(f"actor not oncoming as previous distance is unknown")
            return False # in the first tick there will not be any previous distance
        self.logger.debug(f"actor previous distance {self._previousActorDistances[otherActor.id]} and current distance {self._currentActorDistances[otherActor.id]}")
        if self._previousActorDistances[otherActor.id] > self._currentActorDistances[otherActor.id]: # TODO improve this algorithm
            # self.logger.info(f"actor oncoming")
            return True

        # self.logger.info(f"actor not oncoming")
        return False
    
    def getOncomingVehicles(self):
        if "oncomingVehicles" in self._tickCache:
            return self._tickCache["oncomingVehicles"]

        oncomingVs = []
        for vehicle in self.getVehicles():
            if self.isOncoming(vehicle):
                oncomingVs.append(vehicle)
        self.logger.debug("Oncoming vehicles", oncomingVs)

        self._tickCache["oncomingVehicles"] = oncomingVs
        return self._tickCache["oncomingVehicles"]
    
    def calculateNearestOnComingVehicle(self):

        if "nearestOnComingVehicle" in self._tickCache:
            return self._tickCache["nearestOnComingVehicle"]

        oncomingVs = self.getOncomingVehicles()
        minD = 999999
        minVehicle = None
        for vehicle in oncomingVs:
            currentDistance = self.getCurrentDistance(vehicle)
            if currentDistance < minD:
                minD = currentDistance
                minVehicle = vehicle

        self._tickCache["nearestOnComingVehicle"] = minVehicle

        return self._tickCache["nearestOnComingVehicle"]
    
    def distanceFromNearestOncomingVehicle(self):
        """Can be negative when the front crosses the conflict point

        Returns:
            [type]: [description]
        """
        # TODO we are now just measuring distance from all actors
        vehicle = self.nearestOncomingVehicle
        if vehicle is None:
            self.logger.info(f"No oncoming vehicle")
            return None
        distance = self.getCurrentDistance(vehicle)
        self.logger.debug(f"Distance from nearest oncoming vehicle = {distance}")
        return distance - 2.3 # meter offset for front of the oncoming vehicle.

    def pedTTCNearestOncomingVehicle(self):
        """Fix this method. When there is no collision, TTC must be None. Put it in cache.

        Returns:
            [type]: [description]
        """
        if "TTCNearestOncomingVehicle" in self._tickCache:
            return self._tickCache["TTCNearestOncomingVehicle"]
        

        vehicle = self.nearestOncomingVehicle
        if vehicle is None:
            return None

        vel1 = vehicle.get_velocity()
        start1 = self.getBBVertexInTravelDirection(vehicle)
        vel2 = self.actor.get_velocity()
        start2 = self.actor.get_location()

        collisionPoint, TTC = Utils.getCollisionPointAndTTC(vel1, start1, vel2, start2)

        self._tickCache["TTCNearestOncomingVehicle"] = TTC
        self._tickCache["collisionPoint"] = collisionPoint


        return self._tickCache["TTCNearestOncomingVehicle"]

    def getConflictPoint(self, otherActor):
        if "conflictPoint" in self._tickCache:
            return self._tickCache["conflictPoint"]

        vel1 = otherActor.get_velocity()
        start1 = self.getBBVertexInTravelDirection(otherActor)
        vel2 = self.actor.get_velocity()
        start2 = self.actor.get_location()

        self._tickCache["conflictPoint"] = Utils.getConflictPoint(vel1, start1, vel2, start2)

        return self._tickCache["conflictPoint"]
        


    def getCollisionPoint(self, otherActor):
        if "collisionPoint" in self._tickCache:
            return self._tickCache["collisionPoint"]

        vel1 = otherActor.get_velocity()
        start1 = self.getBBVertexInTravelDirection(otherActor)
        vel2 = self.actor.get_velocity()
        start2 = self.actor.get_location()

        collisionPoint, TTC = Utils.getCollisionPointAndTTC(vel1, start1, vel2, start2)

        self._tickCache["TTCNearestOncomingVehicle"] = TTC
        self._tickCache["collisionPoint"] = collisionPoint

        return self._tickCache["collisionPoint"]
        
       
    def pedTGNearestOncomingVehicle(self):
        """Time gap is different than TTC.

        Returns:
            [type]: [description]
        """
        if "TGNearestOncomingVehicle" in self._tickCache:
            return self._tickCache["TGNearestOncomingVehicle"]

        vehicle = self.nearestOncomingVehicle
        if vehicle is None:
            return None
            
        wp_distance = self.distanceFromNearestOncomingVehicle()
        velocity = vehicle.get_velocity()
        speed = velocity.length()
        if speed < 0.001:
            return None

        TG = wp_distance / speed
        self._tickCache["TGNearestOncomingVehicle"] = TG

        return self._tickCache["TGNearestOncomingVehicle"]
    
    def getBBVertexInTravelDirection(self, bbActor):
        """Can be head or rearend

        Args:
            bbActor ([type]): An actor with a bounding box property
        """
        
        # TODO we can also get the vertice vectors and find the one most parallel to direction.
        location = bbActor.get_location()
        direction = bbActor.get_velocity().make_unit_vector()
        extent = Utils.getMaxExtent(bbActor)
        extentVector = direction * extent

        return location + extentVector


    #endregion

    #region dynamic actor ops
    def getLinearSpeed(self, actor):
        distanceTraveled = abs(self._currentActorDistances[actor.id] - self._previousActorDistances[actor.id])
        speed = distanceTraveled / self.time_delta
        self.logger.info(f"Actor linear speed {speed}")
        return speed

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
