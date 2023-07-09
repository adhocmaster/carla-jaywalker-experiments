import pytest
from agents.pedestrians.soft import NavPath, NavPoint
from agents.pedestrians.soft.LaneSection import LaneSection
from agents.pedestrians.soft.Side import Side
from .fixtures import *

def test_nav_point_psi004(nav_path_psi004):

    # test behavior matching
    # test adaptation.
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
    

    pass