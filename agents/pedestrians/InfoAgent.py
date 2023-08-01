import math
import carla
from lib import LoggerFactory
from lib.utils import Utils
from .PedState import PedState
from shapely.geometry import Point
from shapely.affinity import rotate
# from .planner.PedestrianPlanner import PedestrianPlanner

class InfoAgent:
    def __init__(self, name, walker, config=None):
        self._walker = walker
        # self._acceleration = 1 #m/s^2
        self._localPlanner = None
        # self._localPlanner:PedestrianPlanner = None

        self._logger = LoggerFactory.create(name, config)
        if "debug" in config:
            self.debug = config["debug"]
        else:
            self.debug = False
        
        self._localAxisYaw = None
        self._localYDirection = None


    def getInternalFactor(self, name):
        return self._localPlanner.getInternalFactor(name)

    def setInternalFactor(self, name, val):
        self._localPlanner.setInternalFactor(name, val)

    @property
    def id(self):
        return self.walker.id

    @property
    def logger(self):
        return self._logger
    
    @property
    def actor(self):
        return self._walker
        
    @property
    def walker(self):
        return self._walker
        
    @property
    def control(self):
        return self._walker.get_control()
        
    @property
    def location(self):
        return self._walker.get_location()

    @property
    def velocity(self):
        return self._walker.get_velocity()

    @property
    def speed(self):
        return self._walker.get_velocity().length()

    @property
    def direction(self):
        # TODO: we can use transform
        direction = self.control.direction
        if direction is None:
            return self.velocity.make_unit_vector()
        return direction


    @property
    def feetLocation(self):
        actorLocation = self.location
        return carla.Location(x = actorLocation.x, y = actorLocation.y, z=0.05)

    @property
    def getHeadLocation(self):
        raise Exception("Not implemented yet")

    
    @property
    def localAxisYaw(self) -> float:

        if self._localAxisYaw is None:
            wp = self.map.get_waypoint(self.location)
            wpTransform = wp.transform
            self._localAxisYaw = wpTransform.rotation.yaw
        return self._localAxisYaw
    
    @property
    def localYDirection(self) -> carla.Vector3D:
        """This needs to be invalidated when actor is reset.

        Raises:
            ValueError: _description_

        Returns:
            carla.Vector3D: _description_
        """
        if self._localYDirection is None:
            # degreeAngle = self.localAxisYaw
            # globalY = Point(0,1)
            # localY = rotate(globalY, degreeAngle, use_radians=False)
            # self._localYDirection = carla.Vector3D(x=localY.x, y=localY.y, z=0.0)
            wp = self.map.get_waypoint(self.location)
            crosswalkVector = wp.transform.get_right_vector() # this might actually be in the opposite direction
            desVector = self.destination - self.location

            # it's a component of the destVecotr on crosswalkVector

            # if crosswalkVector.x * desVector.x < 0 and crosswalkVector.y * desVector.y < 0:
            #     crosswalkVector = -crosswalkVector

            angleWithDest = Utils.angleBetweenVectors(crosswalkVector, desVector)

            if abs(angleWithDest) > math.pi/2:
                crosswalkVector = -1 * crosswalkVector
            
            self._localYDirection = crosswalkVector

            # self.visualizer.drawForce(self.location + carla.Location(x=-2.0), crosswalkVector, color=(20,0,20), life_time=20.0)
            # self.visualizer.drawForce(self.location + carla.Location(x=2.0), self._localYDirection, color=(0,0,20), life_time=20.0)
            # self.visualizer.drawForce(self.location + carla.Location(x=4.0), desVector.make_unit_vector(), color=(0,20,0), life_time=20.0)
            # raise ValueError(f"angleWithDest {angleWithDest}")


        return self._localYDirection
    

    def reset(self):
        self._localAxisYaw = None
        self._localYDirection = None



    def updateLogLevel(self, newLevel):
        self.logger.warn(f"Updating {self.name} log level: {newLevel}")
        self._logger = LoggerFactory.create(self.name, {"LOG_LEVEL": newLevel}) # TODO name is not defined in this

    def onTickStart(self, world_snapshot):
        self._localPlanner.onTickStart(world_snapshot)


    
    # def set_destination(self, destination):
    #     """
    #     This method creates a list of waypoints between a starting and ending location,
    #     based on the route returned by the global router, and adds it to the local planner.
    #     If no starting location is passed, the vehicle local planner's target location is chosen,
    #     which corresponds (by default), to a location about 5 meters in front of the vehicle.

    #         :param end_location (carla.Location): final location of the route
    #         :param start_location (carla.Location): starting location of the route
    #     """
        
    #     location = self.location
    #     destination.z = location.z # agent z is in the center of mass, not on the road.
    #     self._destination = destination
        
        
    # def directionToDestination(self) -> carla.Vector3D:
    #     """Calculates direction from the feet of the pedestrians

    #     Returns:
    #         carla.Vector3D: [description]
    #     """
    #     currentLocation = self.feetLocation
    #     distance = self.getDistanceToDestination()

    #     direction = carla.Vector3D(
    #         x = (self._destination.x - currentLocation.x) / distance,
    #         y = (self._destination.y - currentLocation.y) / distance,
    #         z = (self._destination.z - currentLocation.z) / distance
    #     )
    #     return direction

    
    # def getDistanceToDestination(self):
    #     return self._walker.get_location().distance(self._destination)


    def getOldSpeed(self):
        oldControl = self._walker.get_control()
        return oldControl.speed

    def getOldControl(self) -> carla.WalkerControl:
        return self._walker.get_control()

    def getOldVelocity(self) -> carla.Vector3D:
        oldControl = self.getOldControl()
        direction = oldControl.direction
        speed = self.getOldSpeed()
        return carla.Vector3D(direction.x * speed, direction.y * speed, direction.z * speed)

    
    def speedToVelocity(self, speed) -> carla.Vector3D:
        oldControl = self._walker.get_control()
        direction = oldControl.direction
        return carla.Vector3D(direction.x * speed, direction.y * speed, direction.z * speed)


    #region planner interfaces

    def setLocalPlanner(self, planner: any):
        self._localPlanner = planner

        
    @property
    def destination(self):
        return self._localPlanner.destination

    def setDestination(self, destination: carla.Location):
        self._localPlanner.setDestination(destination)

    @property
    def previousLocations(self):
        return self._localPlanner.locations

    
    def updateModelCoeff(self, name, val):
        self._localPlanner.updateModelCoeff(name, val)
    
    def getModels(self, state=None):

        if state is None:
            return self._localPlanner.models
        elif state == PedState.CROSSING:
            return self.getCrossingFactorModels()
        elif state == PedState.SURVIVAL:
            return self.getSurvivalModels()
        else:
            raise Exception(f"No model for the state {state.value}")
        

    def getStateTransitionModels(self):
        return self._localPlanner.stateTransitionModels

    def getCrossingFactorModels(self):
        return self._localPlanner.crossingFactorModels

    def getSurvivalModels(self):
        return self._localPlanner.survivalModels

    #endregion