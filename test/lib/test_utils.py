import pytest
from shapely.geometry import LineString

def test_lineIntersection():

    line1 = LineString([(0, 0), [5,5]])
    line2 = LineString([(1,0), (0,1)])
    line3 = LineString([(10,1), (100, 10)])

    assert line1.intersects(line2)
    assert line2.intersects(line1)
    assert line1.intersects(line3) ==  False
    intersectionPoint = line1.intersection(line2)
    print(type(intersectionPoint), intersectionPoint)
    
    intersectionPoint = line1.intersection(line3)
    print(type(intersectionPoint), intersectionPoint)
    assert False