from msilib.schema import Error
import time
import carla
import logging
from .PedestrianFactory import PedestrianFactory

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
        self.name = f"PedestrianAgent #{walker.id}"
        self._world = self._walker.get_world()
        self._map = self._world.get_map()

        self.skip_ticks = skip_ticks
        self.tickCounter = 0

        self._acceleration = 1 #m/s^2
        self._target_speed = target_speed
        self._destination = None

        self.onSideWalk = True
        self._needJump = False
        self._last_jumped = time.time_ns()

        self.collisionSensor = None
        self.obstacleDetector = None
        self.initSensors()

    
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

    def canJump(self):
        if self.timeSinceLastJumpMS() < 1000:
            return False

        distance = self.distanceToNextSideWalk()
        walkerSpeed = self.getOldSpeed()

        if distance < walkerSpeed * 2 and distance > walkerSpeed:
            return True
        return False

    def updateJumped(self):
        self._last_jumped = time.time_ns()

    def timeSinceLastJumpMS(self):
        diff = (time.time_ns() - self._last_jumped) // 1_000_000 
        return diff


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


    def printLocations(self):
        print("Agent location", self._walker.get_location())
        print("Collision location", self.collisionSensor.get_location())
        print("Obstacle detector location", self.obstacleDetector.get_location())

    def calculateControl(self):
        if self._destination is None:
            raise Error("Destination is none")

        # self.printLocations()
        # self.distanceToNextSideWalk()

        print("Calculating control for Walker {self._walker.id}")
        direction = self.calculateDirectionToDestination()
        speed = self.calculateNextSpeed(direction)

        print(f"Walker {self._walker.id}: distance to destination is {self.getDistanceToDestination()} meters, and next speed {speed}")


        jump = False
        
        if self.canJump():
            self.updateJumped()
            jump = True
            logging.info(f"{self.name} making a jump.")
        # if self._needJump:
        #     logging.info(f"{self.name} need a jump.")
        #     if self.canJump():
        #         self.updateJumped()
        #         jump = True
        #         logging.info(f"{self.name} making a jump.")

        control = carla.WalkerControl(
            direction = direction,
            speed = speed,
            jump = jump
        )

        self._needJump = False

        return control


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


    def getOldSpeed(self):
        oldControl = self._walker.get_control()
        return oldControl.speed

    def calculateNextSpeed(self, direction):

        # TODO make a smooth transition
        oldControl = self._walker.get_control()
        currentSpeed = oldControl.speed
        # nextSpeed = max()
        return self._target_speed


    #region sidewalk


    def getObstaclesToDistance(self):
        actorLocation = self._walker.get_location()
        labeledObjects = self._world.cast_ray(actorLocation, self._destination)
        # for lb in labeledObjects:
        #     print(f"Labeled point location {lb.location} and semantic {lb.label} distance {actorLocation.distance(lb.location)}")
        return labeledObjects
    
    def distanceToNextSideWalk(self):
        actorLocation = self._walker.get_location()
        actorXYLocation = carla.Location(x = actorLocation.x, y = actorLocation.y, z=0.)
        labeledObjects = self.getObstaclesToDistance()
        for lb in labeledObjects:
            if lb.label == carla.CityObjectLabel.Sidewalks:
                sidewalkXYLocation = carla.Location(x = lb.location.x, y = lb.location.y, z=0.)
                print(f"Sidewalk location {lb.location} and semantic {lb.label} XY distance {actorXYLocation.distance(sidewalkXYLocation)}")
                return actorLocation.distance(lb.location)

    #endregion
    #region sensors


    def initSensors(self):
        pedFactor = PedestrianFactory(self._world)
        logging.info(f"{self.name}: adding collision detector")
        self.collisionSensor = pedFactor.addCollisonSensor(self._walker)
        self.collisionSensor.listen(lambda data: self.handleWalkerCollision(data))

        # self.obstacleDetector = pedFactor.addObstacleDetector(self.walker)
        # self.obstacleDetector.listen(lambda data: self.handWalkerObstacles(data))

    def handleWalkerCollision(self, data):
        if self.isSidewalk(data.other_actor):
            logging.info(f"{self.name} hits a sidewalk")
            self._needJump = True
        else:
            logging.info(f"{self.name} hits a non-sidewalk")


    def handWalkerObstacles(self, data):
        # logging.info(f"{self.name} sees a obstackle {data.distance}m away with semantic tag {data.other_actor.semantic_tags}")
        # logging.info("semantic tag", data.other_actor.semantic_tags)
        # if self.isSidewalk(data.other_actor):

        #     if data.distance < 0.1:
        #         logging.info(f"{self.name} is on a sidewalk {data.distance}m away")
        #         self.onSideWalk = True
        #     else:
        #         logging.info(f"{self.name} sees a obstackle {data.distance}m away")
        #         self.onSideWalk = False

        #     # self._needJump = True
        return
    
    def isSidewalk(self, actor):
        if 8 in actor.semantic_tags:
            return True
        return False

    