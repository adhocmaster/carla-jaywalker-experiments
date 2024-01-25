import pytest
from agents.pedestrians.soft import NavPath, NavPoint
from agents.pedestrians.soft.Direction import Direction
from agents.pedestrians.soft.LaneSection import LaneSection
from agents.pedestrians.soft.Side import Side
from .fixtures import *

def test_nav_point_psi004(nav_path_psi004):

    point1 = nav_path_psi004.path[0]
    point2 = nav_path_psi004.path[1]
    point3 = nav_path_psi004.path[2]
    point4 = nav_path_psi004.path[3]

    assert point1.getOtherSide(point2) ==  Side.LEFT
    assert point1.getOtherSide(point3) ==  Side.LEFT
    assert point1.getOtherSide(point4) ==  Side.SAME

    assert point2.getOtherSide(point1) ==  Side.RIGHT
    assert point2.getOtherSide(point3) ==  Side.RIGHT
    assert point2.getOtherSide(point4) ==  Side.RIGHT

    assert point3.getOtherSide(point1) ==  Side.RIGHT
    assert point3.getOtherSide(point2) ==  Side.LEFT
    assert point3.getOtherSide(point4) ==  Side.RIGHT

    assert point4.getOtherSide(point1) ==  Side.SAME
    assert point4.getOtherSide(point2) ==  Side.LEFT
    assert point4.getOtherSide(point3) ==  Side.LEFT
    

def test_nav_point_psi002(nav_path_psi002):

    # test behavior matching
    # test adaptation.
    point1 = nav_path_psi002.path[0]
    point2 = nav_path_psi002.path[1]
    point3 = nav_path_psi002.path[2]
    point4 = nav_path_psi002.path[3]

    assert point1.getOtherSide(point2) ==  Side.RIGHT
    assert point1.getOtherSide(point3) ==  Side.RIGHT
    assert point1.getOtherSide(point4) ==  Side.RIGHT

    assert point2.getOtherSide(point1) ==  Side.LEFT
    assert point2.getOtherSide(point3) ==  Side.SAME
    assert point2.getOtherSide(point4) ==  Side.RIGHT

    assert point3.getOtherSide(point1) ==  Side.LEFT
    assert point3.getOtherSide(point2) ==  Side.SAME
    assert point3.getOtherSide(point4) ==  Side.RIGHT

    assert point4.getOtherSide(point1) ==  Side.LEFT
    assert point4.getOtherSide(point2) ==  Side.LEFT
    assert point4.getOtherSide(point3) ==  Side.LEFT

def test_nav_point_steps_to_adjacent_lanes():
    
    point = NavPoint(
        laneId=1,
        laneSection=LaneSection.LEFT,
        distanceToEgo=20.0, 
        speed=1,
        direction=Direction.RL
    )

    assert point.stepsToLeftLane() == 1
    assert point.stepsToRightLane() == 3

    point = NavPoint(
        laneId=0,
        laneSection=LaneSection.LEFT,
        distanceToEgo=20.0, 
        speed=1,
        direction=Direction.LR
    )

    assert point.stepsToLeftLane() == 1
    assert point.stepsToRightLane() == 3

    point = NavPoint(
        laneId=1,
        laneSection=LaneSection.RIGHT,
        distanceToEgo=20.0, 
        speed=1,
        direction=Direction.RL
    )

    assert point.stepsToLeftLane() == 3

    assert point.stepsToRightLane() == 1
    point = NavPoint(
        laneId=1,
        laneSection=LaneSection.MIDDLE,
        distanceToEgo=20.0, 
        speed=1,
        direction=Direction.RL
    )

    assert point.stepsToLeftLane() == 2
    assert point.stepsToRightLane() == 2


def test_steps_to_other_nav_points():

    # same lane tests
    point1 = NavPoint(
        laneId=1,
        laneSection=LaneSection.LEFT,
        distanceToEgo=20.0, 
        speed=1,
        direction=Direction.LR
    )
    point2 = NavPoint(
        laneId=1,
        laneSection=LaneSection.LEFT,
        distanceToEgo=20.0, 
        speed=1,
        direction=Direction.LR
    )

    assert point1.getStepsToOther(point2) == 0
    assert point2.getStepsToOther(point1) == 0

    
    point1 = NavPoint(
        laneId=1,
        laneSection=LaneSection.MIDDLE,
        distanceToEgo=20.0, 
        speed=1,
        direction=Direction.LR
    )
    assert point1.getStepsToOther(point2) == 1
    assert point2.getStepsToOther(point1) == 1

    
    point1 = NavPoint(
        laneId=1,
        laneSection=LaneSection.RIGHT,
        distanceToEgo=20.0, 
        speed=1,
        direction=Direction.LR
    )
    assert point1.getStepsToOther(point2) == 2
    assert point2.getStepsToOther(point1) == 2

    # adjacent lane tests
    
    for steps, laneSectionL1 in zip([3, 4, 5], [LaneSection.LEFT, LaneSection.MIDDLE, LaneSection.RIGHT]):
        point1 = NavPoint(
            laneId=1,
            laneSection=laneSectionL1,
            distanceToEgo=20.0, 
            speed=1,
            direction=Direction.LR
        )
        for laneSectionL0 in [LaneSection.LEFT, LaneSection.MIDDLE, LaneSection.RIGHT]:
            point0 = NavPoint(
                laneId=0,
                laneSection=laneSectionL0,
                distanceToEgo=20.0, 
                speed=1,
                direction=Direction.LR
            )

            assert point1.getStepsToOther(point0) == steps
            assert point0.getStepsToOther(point1) == steps
            steps -= 1

        
    # non-adjacent lane tests
    
    for steps, laneSectionL1 in zip([6, 7, 8], [LaneSection.LEFT, LaneSection.MIDDLE, LaneSection.RIGHT]):
        point1 = NavPoint(
            laneId=1,
            laneSection=laneSectionL1,
            distanceToEgo=20.0, 
            speed=1,
            direction=Direction.LR
        )
        for laneSectionL0 in [LaneSection.LEFT, LaneSection.MIDDLE, LaneSection.RIGHT]:
            point0 = NavPoint(
                laneId=-1,
                laneSection=laneSectionL0,
                distanceToEgo=20.0, 
                speed=1,
                direction=Direction.LR
            )

            # print(laneSectionL1, laneSectionL0, point1.getStepsToOther(point0))
            assert point1.getStepsToOther(point0) == steps
            assert point0.getStepsToOther(point1) == steps
            steps -= 1

    for steps, laneSectionL1 in zip([6, 5, 4], [LaneSection.LEFT, LaneSection.MIDDLE, LaneSection.RIGHT]):
        point1 = NavPoint(
            laneId=1,
            laneSection=laneSectionL1,
            distanceToEgo=20.0, 
            speed=1,
            direction=Direction.LR
        )
        for laneSectionL0 in [LaneSection.LEFT, LaneSection.MIDDLE, LaneSection.RIGHT]:
            point0 = NavPoint(
                laneId=3,
                laneSection=laneSectionL0,
                distanceToEgo=20.0, 
                speed=1,
                direction=Direction.LR
            )

            print(laneSectionL1, laneSectionL0, point1.getStepsToOther(point0))
            assert point1.getStepsToOther(point0) == steps
            assert point0.getStepsToOther(point1) == steps
            steps += 1
    # assert False