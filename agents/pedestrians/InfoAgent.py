import carla
from lib import LogProducer, LoggerFactory

class InfoAgent:
    def __init__(self, name, walker, desired_speed=1.5, config=None):
        self._walker = walker
        self.desired_speed = desired_speed
        # self._acceleration = 1 #m/s^2
        self._destination = None

        self._logger = LoggerFactory.create(name, config)

    @property
    def logger(self):
        return self._logger
    
    @property
    def walker(self):
        return self._walker

        
    @property
    def location(self):
        return self._walker.get_location()

    @property
    def feetLocation(self):
        actorLocation = self.location
        return carla.Location(x = actorLocation.x, y = actorLocation.y, z=0.05)

    @property
    def getHeadLocation(self):
        raise Exception("Not implemented yet")



        
    @property
    def destination(self):
        return self._destination

    
    def set_destination(self, destination):
        """
        This method creates a list of waypoints between a starting and ending location,
        based on the route returned by the global router, and adds it to the local planner.
        If no starting location is passed, the vehicle local planner's target location is chosen,
        which corresponds (by default), to a location about 5 meters in front of the vehicle.

            :param end_location (carla.Location): final location of the route
            :param start_location (carla.Location): starting location of the route
        """
        
        location = self.location
        destination.z = location.z # agent z is in the center of mass, not on the road.
        self._destination = destination
        
        
    def directionToDestination(self) -> carla.Vector3D:
        currentLocation = self.feetLocation
        distance = self.getDistanceToDestination()

        direction = carla.Vector3D(
            x = (self._destination.x - currentLocation.x) / distance,
            y = (self._destination.y - currentLocation.y) / distance,
            z = (self._destination.z - currentLocation.z) / distance
        )
        return direction

    
    def getDistanceToDestination(self):
        return self._walker.get_location().distance(self._destination)


    def getOldSpeed(self):
        oldControl = self._walker.get_control()
        return oldControl.speed

    
    def getOldVelocity(self) -> carla.Vector3D:
        oldControl = self._walker.get_control()
        direction = oldControl.direction
        speed = self.getOldSpeed()
        return carla.Vector3D(direction.x * speed, direction.y * speed, direction.z * speed)

    
    def speedToVelocity(self, speed) -> carla.Vector3D:
        oldControl = self._walker.get_control()
        direction = oldControl.direction
        return carla.Vector3D(direction.x * speed, direction.y * speed, direction.z * speed)