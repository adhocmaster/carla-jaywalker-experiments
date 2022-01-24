from msilib.schema import Error
import carla

class PedestrianAgent:
    
    def __init__(self, walker, target_speed=1.5, skip_ticks=10, opt_dict={}):
        """
        Initialization the agent paramters, the local and the global planner.

            :param walker: actor to apply to agent logic onto
            :param target_speed: speed (in m/s) at which the vehicle will move range is (0.7-5.7) Pedestrian acceleration and speeds, 2012
            :param opt_dict: dictionary in case some of its parameters want to be changed.
                This also applies to parameters related to the LocalPlanner.
        """
        self._walker = walker
        self._world = self._walker.get_world()
        self._map = self._world.get_map()

        self.skip_ticks = skip_ticks
        self.tickCounter = 0

        self._acceleration = 1 #m/s^2
        self._target_speed = target_speed
        self._destination = None

    
    @property
    def walker(self):
        return self._walker


    def set_target_speed(self, target_speed):
        self._target_speed = target_speed
    
    def set_destination(self, destination):
        """
        This method creates a list of waypoints between a starting and ending location,
        based on the route returned by the global router, and adds it to the local planner.
        If no starting location is passed, the vehicle local planner's target location is chosen,
        which corresponds (by default), to a location about 5 meters in front of the vehicle.

            :param end_location (carla.Location): final location of the route
            :param start_location (carla.Location): starting location of the route
        """
        
        self._destination = destination


    def done(self):
        if self.getDistanceToDestination() < 0.1:
            return True
        return False

    def canUpdate(self):
        self.tickCounter += 1
        if self.tickCounter >= self.skip_ticks:
            self.tickCounter = 0
            return True
        return False
    
    def updateControl(self):
        "we should not call this. apply batch control"
        self._walker.apply_control(self.calculateControl())


    def calculateControl(self):
        if self._destination is None:
            raise Error("Destination is none")

        print("Calculating control for Walker {self._walker.id}")
        direction = self.calculateDirectionToDestination()
        speed = self.calculateNextSpeed(direction)

        print(f"Walker {self._walker.id}: distance to destination is {self.getDistanceToDestination()} meters, and next speed {speed}")

        return carla.WalkerControl(
            direction = direction,
            speed = speed,
            jump = False
        )


    def calculateDirectionToDestination(self) -> carla.Vector3D:
        currentLocation = self._walker.get_location()
        distance = self.getDistanceToDestination()

        direction = carla.Vector3D(
            x = (self._destination.x - currentLocation.x) / distance,
            y = (self._destination.y - currentLocation.y) / distance,
            z = (self._destination.z - currentLocation.z) / distance
        )
        return direction

    
    def getDistanceToDestination(self):
        return self._walker.get_location().distance(self._destination)

    def calculateNextSpeed(self, direction):

        # TODO make a smooth transition
        oldControl = self._walker.get_control()
        currentSpeed = oldControl.speed
        # nextSpeed = max()
        return self._target_speed




