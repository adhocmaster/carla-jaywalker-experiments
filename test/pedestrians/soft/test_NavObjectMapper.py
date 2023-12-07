import json
import pytest

from agents.pedestrians.soft import LaneSection, NavObjectMapper

@pytest.fixture()
def navPathJSON() -> str:
    path = "data/navpath/nav_path_straight_road.json"
    with open(path, "r") as f:
        return f.read()
    
@pytest.fixture()
def navPathJSONGroup() -> str:
    path = "data/navpath/nav_path_straight_road_group.json"
    with open(path, "r") as f:
        return f.read()
    

def test_jsonToNavPaths(navPathJSON):
    # print("navPathJSON", navPathJSON)
    dicts = json.loads(navPathJSON)
    navPaths = NavObjectMapper.pathsFromDicts(dicts)
    # print(navPaths)
    assert len(navPaths) > 0
    firstPah = navPaths[0]
    assert firstPah.id == "psi-0002"
    assert firstPah.roadWidth == 7.0
    assert firstPah.nEgoDirectionLanes == 1
    assert firstPah.nEgoOppositeDirectionLanes == 1

    assert len(firstPah.path) == 4
    firstPoint = firstPah.path[0]
    assert firstPoint.laneId == -1
    assert firstPoint.laneSection == LaneSection.LEFT
    assert firstPoint.distanceToEgo == 24.0
    assert firstPoint.distanceToInitialEgo == 24.0


def test_groupNavPaths(navPathJSONGroup):
    dicts = json.loads(navPathJSONGroup)
    navPaths = NavObjectMapper.pathsFromDicts(dicts)
    # for navPath in navPaths:
    #     print(navPath)

    firstPath = navPaths[0]
    assert firstPath.id == "psi-0048-0"
    # assert False
    