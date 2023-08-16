
from agents.pedestrians.soft import *
from research.Research1v1 import Research1v1


class Research1v1NavPathModel(Research1v1):
    
    
    def createWalker(self):
        
        super().createWalker()
        
        self.walkerAgent.setEgoVehicle(self.vehicle)
        self.setWalkerNavPath()
        pass

    
    def resetWalker(self, sameOrigin=True):
        super().resetWalker()
        
        self.walkerAgent.setEgoVehicle(self.vehicle)
        self.setWalkerNavPath()
        pass

    
    def setWalkerNavPath(self):
        
        point1 = NavPoint(
            NavPointLocation(
                laneId=-1,
                laneSection=LaneSection.LEFT,
                distanceToEgo=24.0, 
                distanceToInitialEgo=24.0, 
            ),
            NavPointBehavior(
                speed=1
            )
        )

        point2 = NavPoint(
            NavPointLocation(
                laneId=-1,
                laneSection=LaneSection.MIDDLE,
                distanceToEgo=7.0, 
                distanceToInitialEgo=25.0, 
            ),
            NavPointBehavior(
                speed=0.5
            )
        )

        point3 = NavPoint(
            NavPointLocation(
                laneId=-1,
                laneSection=LaneSection.MIDDLE,
                distanceToEgo=1.0, 
                distanceToInitialEgo=25.0, 
            ),
            NavPointBehavior(
                speed=0.1
            )
        )


        point4 = NavPoint(
            NavPointLocation(
                laneId=0,
                laneSection=LaneSection.LEFT,
                distanceToEgo=-1, 
                distanceToInitialEgo=25.0, 
            ),
            NavPointBehavior(
                speed=1
            )
        )


        roadConfiguration = NavPathRoadConfiguration(
            roadWidth=2 * 3.5,
            nEgoDirectionLanes=1,
            nEgoOppositeDirectionLanes=1
        )

        egoConfiguration = NavPathEgoConfiguration(
            egoLaneWrtCenter = 1,
            egoSpeedStart=10,
            egoSpeedEnd=20
        )

        pedConfiguration = NavPathPedestrianConfiguration(
            
            direction=Direction.LR,
            avgSpeed=0.5,
            maxSpeed=1.5,
            minSpeed=0.0
        )
            
            

        navPath = NavPath(
            id="psi-002",
            roadConfiguration=roadConfiguration,
            egoConfiguration=egoConfiguration,
            pedConfiguration=pedConfiguration,
            path=[point1, point2, point3, point4]
        )
        self.walkerAgent.setNavPath(navPath)
