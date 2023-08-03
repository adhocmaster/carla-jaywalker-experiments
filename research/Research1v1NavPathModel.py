
from agents.pedestrians.soft import NavPointLocation, NavPointBehavior, LaneSection, Direction, NavPath, NavPoint
from research.Research1v1 import Research1v1


class Research1v1NavPathModel(Research1v1):
    
    
    def createWalker(self):
        
        super().createWalker()
        self.setWalkerNavPath()
        pass

    
    def resetWalker(self, sameOrigin=True):
        super().resetWalker()
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
                speed=1,
                direction=Direction.LR
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
                speed=0.5,
                direction=Direction.LR
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
                speed=0.1,
                direction=Direction.LR
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
                speed=1,
                direction=Direction.LR
            )
        )

        navPath = NavPath(
            roadWidth=2 * 3.5,
            path=[point1, point2, point3, point4],
            nEgoDirectionLanes=1,
            nEgoOppositeDirectionLanes=1,
            avgSpeed=0.5,
            maxSpeed=1.5,
            minSpeed=0.0,
            egoLaneWrtCenter = 1,
            egoSpeedStart=20,
            egoSpeedEnd=10
        )
        self.walkerAgent.setNavPath(navPath)
