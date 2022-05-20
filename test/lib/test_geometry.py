import carla
import pytest
import numpy as np
import math
from lib.Geometry import Geometry


def test_changeCartesianCenter():

    p = carla.Vector3D(x=5, y=10, z=10)
    center = carla.Vector3D(x=8, y=2, z=2)

    p2 = Geometry.changeCartesianCenter(p, center)

    print(f"transformed x={p2.x}, y={p2.y}, z={p2.z}")

    assert p2.x == -3.0
    assert p2.y == 8
    assert p2.z == 8
    assert p.x == 5.0
    assert p.y == 10.0
    assert p.z == 10.0


def test_rotateAroundZ():
    p = carla.Vector3D(x=5, y=10, z=10)
    center = carla.Vector3D(x=8, y=2, z=2)
    p2 = Geometry.changeCartesianCenter(p, center)

    angle = np.pi/10
    p3 = Geometry.rotateAroundZ(p2, -angle)

    print(f"translated x={p2.x}, y={p2.y}, z={p2.z}")
    print(f"rotated x={p3.x}, y={p3.y}, z={p3.z}")

    p4 = Geometry.changeCartesianCenter(p, center, centerRotation=angle)
    print(f"transformed x={p4.x}, y={p4.y}, z={p4.z}")

    assert p3.x == p4.x
    assert p3.y == p4.y

    # assert False


