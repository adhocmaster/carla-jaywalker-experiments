import pytest
from agents.pedestrians.destination import CrosswalkModel
import shapely.geometry
import matplotlib.pyplot as plt
import math
import random



def test_1():
    #TODO
    # Create crosswalk area as Polygons
    areaPolygon = shapely.geometry.Polygon([(4, 0), (3, 3), (0, 6), (9, 6), (6, 3), (5, 0)])

    # Create start point and end point.
    start = shapely.geometry.Point((4.5, 0))
    end = shapely.geometry.Point((4.5, 6))
    goalLine = shapely.geometry.LineString([(0, 6), (8, 6)])
    crosswalkModel = CrosswalkModel(
        source=start, 
        idealDestination=end, 
        areaPolygon=areaPolygon,
        goalLine=goalLine
        )
        
    pass