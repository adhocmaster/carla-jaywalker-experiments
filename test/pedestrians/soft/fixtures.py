import pytest
from agents.pedestrians.soft import NavPath, NavPoint
from agents.pedestrians.soft.Direction import Direction
from agents.pedestrians.soft.LaneSection import LaneSection

@pytest.fixture
def nav_path_psi004():
    
    path = []
    point1 = NavPoint(
        laneId=1,
        laneSection=LaneSection.LEFT,
        distanceToEgo=20.0, 
        speed=1,
        direction=Direction.LR
    )

    point2 = NavPoint(
        laneId=0,
        laneSection=LaneSection.MIDDLE,
        distanceToEgo=15.0, 
        speed=0.2,
        direction=Direction.LR
    )

    point3 = NavPoint(
        laneId=0,
        laneSection=LaneSection.RIGHT,
        distanceToEgo=6.0, 
        speed=0.8,
        direction=Direction.LR
    )
    point4 = NavPoint(
        laneId=1,
        laneSection=LaneSection.LEFT,
        distanceToEgo=2.0, 
        speed=0.1,
        direction=Direction.LR
    )

    navPath = NavPath(
        roadWidth=4 * 3.5,
        path=[point1, point2, point3, point4],
        nEgoDirectionLanes=2,
        nEgoOppositeDirectionLanes=2,
        avgSpeed=0.5,
        maxSpeed=1,
        minSpeed=0.1
    )

    return navPath

@pytest.fixture
def nav_path_psi002():
    
    path = []
    point1 = NavPoint(
        laneId=-1,
        laneSection=LaneSection.LEFT,
        distanceToEgo=24.0, 
        speed=1,
        direction=Direction.RL
    )
    point2 = NavPoint(
        laneId=-1,
        laneSection=LaneSection.MIDDLE,
        distanceToEgo=7.0, 
        speed=0.5,
        direction=Direction.RL
    )
    
    point3 = NavPoint(
        laneId=-1,
        laneSection=LaneSection.MIDDLE,
        distanceToEgo=1.0, 
        speed=0.1,
        direction=Direction.RL
    )

    
    point4 = NavPoint(
        laneId=0,
        laneSection=LaneSection.LEFT,
        distanceToEgo=-1, 
        speed=0.0,
        direction=Direction.RL
    )

    navPath = NavPath(
        roadWidth=2 * 3.5,
        path=[point1, point2, point3, point4],
        nEgoDirectionLanes=1,
        nEgoOppositeDirectionLanes=1,
        avgSpeed=0.5,
        maxSpeed=1.5,
        minSpeed=0.0
    )

    return navPath