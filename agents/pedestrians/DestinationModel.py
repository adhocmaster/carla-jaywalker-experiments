import carla
from lib import ActorManager, ObstacleManager, Utils
from .ForceModel import ForceModel
from .PedestrianAgent import PedestrianAgent


class DestinationModel(ForceModel):

    def __init__(self, agent: PedestrianAgent, actorManager: ActorManager, obstacleManager: ObstacleManager, final_destination=None, factors = None) -> None:

        super().__init__(agent, actorManager, obstacleManager)

        # self._source = source # source may not be current agent location
        self._finalDestination = final_destination
        self._nextDestination = final_destination

        self.factors = factors

        self.initFactors()

        pass

    
    def initFactors(self):
        if self.factors is None:
            self.factors = {}
        
        if "desired_speed" not in self.factors:
            self.factors["desired_speed"] = 2 

        if "relaxation_time" not in self.factors:
            self.factors["relaxation_time"] = 0.1 
        
        pass

    
    def setFinalDestination(self, destination):
        """
        This method creates a list of waypoints between a starting and ending location,
        based on the route returned by the global router, and adds it to the local planner.
        If no starting location is passed, the vehicle local planner's target location is chosen,
        which corresponds (by default), to a location about 5 meters in front of the vehicle.

            :param end_location (carla.Location): final location of the route
            :param start_location (carla.Location): starting location of the route
        """
        
        self._finalDestination = destination
        # if self._nextDestination is None:
        #     self._nextDestination = destination
        self._nextDestination = destination # TODO what we want to do is keep a destination queue and pop it to next destination when next destination is reached. 
        
            
    def getDistanceToDestination(self):
        return Utils.getDistance(self.agent.feetLocation, self._nextDestination, ignoreZ=True)

    
    def getDesiredVelocity(self) -> carla.Vector3D:
        return self.getDesiredDirection() * self.factors["desired_speed"] 

    def getDesiredSpeed(self) -> carla.Vector3D:
        return self.factors["desired_speed"] 


    def getDesiredDirection(self) -> carla.Vector3D:
        return Utils.getDirection(self.agent.feetLocation, self._nextDestination, ignoreZ=True)
        exit(0)
        return direction
        

    def getDistanceToNextDestination(self):
        return self.agent.getFeetLocation().distance(self._nextDestination)


    def calculateForce(self):
        return self.calculateForceForDesiredVelocity()
    
    def calculateForceForDesiredVelocity(self):
        desiredVelocity = self.getDesiredVelocity()
        oldVelocity = self.agent.getOldVelocity()

        return (desiredVelocity - oldVelocity) / self.factors["relaxation_time"]

    



