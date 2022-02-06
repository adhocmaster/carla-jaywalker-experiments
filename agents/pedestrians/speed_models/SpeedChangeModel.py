from abc import abstractmethod
import numpy as np
from agents.pedestrians.factors import InternalFactors
from lib import ActorManager, ObstacleManager, NotImplementedInterface
from agents.pedestrians.PedestrianAgent import PedestrianAgent
from ..ForceModel import ForceModel
from ..DestinationModel import DestinationModel

class SpeedChangeModel(ForceModel):
    """gender, age group, group-crossing, committing the spatial violation and experiencing conflict have a significant impact on 
    pedestrians crossing speed at unsignalized crosswalks. On the contrary, technological distractions and carrying items had 
    no impact on crossing speed.
    
    Male pedestrians and pedestrians committing spatial violation cross the crosswalk faster. Furthermore, old pedestrians (as compared to young pedestrians) 
    and pedestrians participating in groups (as compared to alone pedestrians) move slower. Finally, pedestrians experiencing 
    conflict finished the crossing slower than the others. This could be because pedestrians experiencing conflict often yielded 
    to the oncoming vehicle for avoiding contingent collision, instead of crossing faster.

    Higher the vehicle speed, higher the crossing speed

    Group norms

    old people more variation

    better speed estimate while crossing

    Abstract away age, group, gender

    Let's define abstract factors

    1. change probability
    2. acceleration/deceleration range
    3. onComing Vehicle force (positive or negative)

    Speed change models only change the speed of the base destination force. Lets assume we can only increase or decrease speed, or change direction orthogonal to the desired direction.
    Also, factors can be turned off and on

    """

    def __init__(
                    self, 
                    destinationModel: DestinationModel,
                    agent: PedestrianAgent, 
                    actorManager: ActorManager, 
                    obstacleManager: ObstacleManager, 
                    internalFactors: InternalFactors
                ) -> None:

        super().__init__(
                            agent, 
                            actorManager, 
                            obstacleManager, 
                            internalFactors
                        )
        self.destinationModel = destinationModel


    def wantChange(self):
        pC = self.internalFactors["speed_change_probability"]
        return np.random.choice([True, False], p =[pC, 1 - pC])

    def getOncomingVehicleForce(self):
        magnitude = self.internalFactors["oncoming_vehicle_speed_force"]
        direction = self.destinationModel.getDesiredDirection()
        return direction * magnitude


    @abstractmethod
    def minSpeed(self):
        return self.internalFactors["min_crossing_speed"]

    @abstractmethod
    def maxSpeed(self):
        return self.internalFactors["max_crossing_speed"]

    @abstractmethod
    def medianSpeed(self):
        return self.internalFactors["median_crossing_speed"]

    @abstractmethod
    def sampleSpeed(self):
        raise NotImplementedInterface("sampleSpeed")

    @abstractmethod
    def desiredSpeed(self):
        raise NotImplementedInterface("desiredSpeed")

    @abstractmethod
    def nextSpeed(self, currentSpeed):
        """A complex relation between desiredSpeed, currentSpeed and sampleSpeed, internal factors, external factors.

        Args:
            currentSpeed ([type]): [description]

        Raises:
            NotImplementedInterface: [description]
        """
        raise NotImplementedInterface("nextSpeed")