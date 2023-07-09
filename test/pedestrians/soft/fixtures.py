import pytest
from agents.pedestrians.soft import NavPath, NavPoint
from agents.pedestrians.soft.LaneSection import LaneSection

@pytest.fixture
def nav_path_psi004():
    
    path = []
    point1 = NavPoint(
        laneId=1,
        laneSection=LaneSection.LEFT,
        distanceToEgo=20.0
    )

    point2 = NavPoint(
        laneId=0,
        laneSection=LaneSection.MIDDLE,
        distanceToEgo=15.0
    )

    point3 = NavPoint(
        laneId=0,
        laneSection=LaneSection.RIGHT,
        distanceToEgo=6.0
    )
    point4 = NavPoint(
        laneId=1,
        laneSection=LaneSection.LEFT,
        distanceToEgo=2.0
    )

    navPath = NavPath(
        roadWidth=4 * 3.5,
        path=[point1, point2, point3, point4],
        nEgoDirectionLanes=2,
        nEgoOppositeDirectionLanes=2
    )

    return navPath