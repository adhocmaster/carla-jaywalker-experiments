from numpy import isin
import pytest
from shapely.geometry import LineString, Point
import carla
from lib.utils import Utils

def test_lineIntersection():

    line1 = LineString([(0, 0), [5,5]])
    line2 = LineString([(1,0), (0,1)])
    line3 = LineString([(10,1), (100, 10)])

    assert line1.intersects(line2)
    assert line2.intersects(line1)
    assert line1.intersects(line3) ==  False
    intersectionPoint = line1.intersection(line2)
    print(type(intersectionPoint), intersectionPoint)
    assert isinstance(intersectionPoint, Point)
    
    intersectionPoint = line1.intersection(line3)
    print(type(intersectionPoint), intersectionPoint)
    assert isinstance(intersectionPoint, LineString)


def test_conflict_point():

    # case 1
    seconds = 10
    vel1 = carla.Vector3D(1, 0, 0)
    start1 =  carla.Location(1, 3, 0)
    
    vel2 = carla.Vector3D(0, 1, 0)
    start2 =  carla.Location(4, 0, 0)

    ls1 = Utils.getLineSegment(vel1, start1, seconds=seconds)

    ls2 = Utils.getLineSegment(vel2, start2, seconds=seconds)

    assert ls1.length >= 10 and ls1.length <= 11
    assert ls2.length >= 10 and ls2.length <= 11

    print(ls1)
    print(ls2)

    conflictPoint = Utils.getConflictPoint(vel1, start1, vel2, start2, seconds)
    print(conflictPoint)

    assert conflictPoint is not None
    assert conflictPoint.x == 4.0
    assert conflictPoint.y == 3.0

    # assert False

    # case 2
    seconds = 1
    vel1 = carla.Vector3D(1, 0, 0)
    start1 =  carla.Location(1, 3, 0)
    
    vel2 = carla.Vector3D(0, 1, 0)
    start2 =  carla.Location(4, 0, 0)

    conflictPoint = Utils.getConflictPoint(vel1, start1, vel2, start2, seconds)

    assert conflictPoint is None

    # case 3
    seconds = 10
    vel1 = carla.Vector3D(1, 1, 0)
    start1 =  carla.Location(1, 1, 0)
    
    vel2 = carla.Vector3D(0, 1, 0)
    start2 =  carla.Location(4, 0, 0)

    conflictPoint = Utils.getConflictPoint(vel1, start1, vel2, start2, seconds)

    print(conflictPoint)
    assert conflictPoint is not None
    assert conflictPoint.x == 4.0
    assert conflictPoint.y == 4.0
    

    # 2022-02-09 13:35:17,732 - PedestrianAgent #171 - INFO - vehicle velo: Vector3D(x=-0.707335, y=3.019205, z=0.166730)
    # 2022-02-09 13:35:17,732 - PedestrianAgent #171 - INFO - vehicle location: Location(x=-155.988235, y=-27.490515, z=0.005021)
    # 2022-02-09 13:35:17,732 - PedestrianAgent #171 - INFO - ped velo: Vector3D(x=0.020926, y=-0.062343, z=0.000000)
    # 2022-02-09 13:35:17,732 - PedestrianAgent #171 - INFO - ped location: Location(x=-149.999222, y=-4.002181, z=1.103900)

    # Utils.drawConflictPointOnGraph(vel1, start1, vel2, start2, seconds)

    seconds = 10
    vel1 = carla.Vector3D(x=1.359963, y=4.535622, z=0.002943)
    start1 =  carla.Location(x=-156.723312, y=-23.485638, z=-0.372956)
    
    vel2 = carla.Vector3D(x=0.602263, y=-1.907165, z=0.000000)
    start2 =  carla.Location(x=-150.000000, y=-4.000000, z=1.103900)

    vel2 = Utils.getVelocityWithNewSpeed(vel2, 2)

    Utils.drawConflictPointOnGraph(vel1, start1, vel2, start2, seconds)


