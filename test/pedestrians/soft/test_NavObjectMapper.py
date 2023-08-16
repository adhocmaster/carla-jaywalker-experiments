import json
import pytest

from agents.pedestrians.soft import LaneSection, NavObjectMapper

@pytest.fixture()
def navPathJSON() -> str:
    path = "settings/nav_path.json"
    with open(path, "r") as f:
        return f.read()
    

def test_jsonToNavPaths(navPathJSON):
    # print("navPathJSON", navPathJSON)
    dicts = json.loads(navPathJSON)
    navPaths = NavObjectMapper.pathsFromDicts(dicts)
    print(navPaths)
    assert len(navPaths) > 0
    firstPah = navPaths[0]
    assert firstPah.id == 1
    assert firstPah.roadWidth == 7.0
    assert firstPah.nEgoDirectionLanes == 1
    assert firstPah.nEgoOppositeDirectionLanes == 1

    assert len(firstPah.path) == 4
    firstPoint = firstPah.path[0]
    assert firstPoint.laneId == -1
    assert firstPoint.laneSection == LaneSection.LEFT
    assert firstPoint.distanceToEgo == 24.0
    assert firstPoint.distanceToInitialEgo == 24.0