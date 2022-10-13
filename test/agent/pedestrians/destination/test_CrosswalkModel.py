import pytest
from agents.pedestrians.destination import CrosswalkModel
from shapely.geometry import Polygon, Point, LineString
from shapely import affinity
import matplotlib.pyplot as plt
import math
import random


def test_1():
    #TODO
    # Create crosswalk area as Polygons
    areaPolygon = Polygon([(4, 0), (3, 3), (0, 6), (9, 6), (6, 3), (5, 0)])

    # Create start point and end point.
    start = Point((4.5, 0))
    end = Point((4.5, 6))
    goalLine = LineString([(0, 6), (8, 6)])
    crosswalkModel = CrosswalkModel(
        source=start, 
        idealDestination=end, 
        areaPolygon=areaPolygon
        )
    
    pass