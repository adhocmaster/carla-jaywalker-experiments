import carla
import argparse
import logging
import random
import time
import eventlet
eventlet.monkey_patch()

from shapely.geometry import Point, LineString, Polygon
from shapely.affinity import scale, rotate

from agents.navigation.behavior_agent import BehaviorAgent  # pylint: disable=import-error
from agents.navigation.basic_agent import BasicAgent  # pylint: disable=import-error

from lib import SimulationVisualization, MapNames, MapManager, Simulator, Geometry

from agents.vehicles import VehicleFactory
from lib.state import StateManager

SpawnActor = carla.command.SpawnActor

argparser = argparse.ArgumentParser()

argparser.add_argument(
    '--host',
    metavar='H',
    default='127.0.0.1',
    help='IP of the host server (default: 127.0.0.1)')
argparser.add_argument(
    '-p', '--port',
    metavar='P',
    default=2000,
    type=int,
    help='TCP port to listen to (default: 2000)')
argparser.add_argument(
    '--tm-port',
    metavar='P',
    default=8000,
    type=int,
    help='Port to communicate with TM (default: 8000)')

args = argparser.parse_args()

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

client = carla.Client(args.host, args.port)
client.set_timeout(5.0)


mapManager = MapManager(client)

visualizer = SimulationVisualization(client, mapManager)
visualizer.draw00()

world = client.get_world()
map = mapManager.map

env_objs = world.get_environment_objects(carla.CityObjectLabel.Buildings)

# 2 ways to get sidewalk
# 1. ray tracing - error prone, obsticles can hide sidewalk, but easy to find relevant sidewalks on the opposite side. But cast_ray may solve this problem
# 2. querying all the sidewalks and use shapely to find relevant ones.

# more issues with ray casting, the sidewalk z values are less than ~ 0.1 meter

# experiments on circular_t_junction
# source = (-113.0, -3.0)
# dest = (-113.0, -14.0)

source = (-106.0, -4.0)
dest = (-106.0, -17.0)
initialLocaltion = carla.Location(source[0], source[1], 0.1)
goalLocation = carla.Location(dest[0], dest[1], 0.1)

visualizer.drawPoint(initialLocaltion, life_time=10.0)
visualizer.drawPoint(goalLocation, life_time=10.0)

# vehicleFactory = VehicleFactory(client, visualizer=visualizer)
# vehicleSpawnPoint = carla.Transform(location = carla.Location(-113.0, -10.0, 10))
# vehicle = vehicleFactory.spawn(vehicleSpawnPoint)   



# we can device a method that works like lider scanning to find points on side walk.
# assume initial location and goalLocation forms the y axis, we make a line longer than the straight line connecting them. Then rotate them and find points on them

# yAxis = LineString([source, dest])

# # iPoint = yAxis.interpolate(50, normalized=False) # extending by 50%

# # scanLine = LineString([source, iPoint])
# centerScanLine = scale(yAxis, xfact=1.5, yfact=1.5, origin=source)
# print(centerScanLine)

# we need to scan sequentially and stop when there is no side walk


def makeCenterScanLine(source: carla.Location, dest: carla.Location):

    s = (source.x, source.y)
    d = (dest.x, dest.y)
    yAxis = LineString([s, d])
    centerScanLine = scale(yAxis, xfact=1.5, yfact=1.5, origin=s)
    return centerScanLine


def getSideWalkPoint(scanLine: LineString) -> Point:
    
    initialLocaltion = carla.Location(scanLine.coords[0][0], scanLine.coords[0][1], 0.1)
    endLocation = carla.Location(scanLine.coords[1][0], scanLine.coords[1][1], 0.1)
    objectsInPath = world.cast_ray(initialLocaltion, endLocation)
    for obj in objectsInPath:
        # print(f"type: {obj.label}, position: {obj.location}")
        if obj.label == carla.CityObjectLabel.Sidewalks:
            sideWalkLine = LineString([scanLine.coords[0], (obj.location.x, obj.location.y)])
            scaleFactor = (sideWalkLine.length + 1) / sideWalkLine.length
            sideWalkLine = scale(sideWalkLine, xfact=scaleFactor, yfact=scaleFactor, origin=scanLine.coords[0])
            return sideWalkLine.coords[1]
    
    return None


def getScanLinesAndSidewalkPoints(centerScanLine: LineString):
    """Sequentially searches for sidewalk from the center scan line. whenever it cannot detect a sidewalk, the search stops.

    Args:
        centerScanLine (LineString): line between the origin and the ideal destination

    Returns:
        _type_: _description_
    """
    
    rightScanLines = []
    rightSideWalkPoints = []
    for i in range(1, 10):
        angle = 10 * i
        newLine = rotate(centerScanLine, angle, origin=source)
        sideWalkPoint = getSideWalkPoint(newLine)
        if sideWalkPoint is not None:
            rightScanLines.append(newLine)
            rightSideWalkPoints.append(sideWalkPoint)
        else:
            break
    
    
    leftScanLines = []
    leftSideWalkPoints = []
    for i in range(1, 10):
        angle = -10 * i
        newLine = rotate(centerScanLine, angle, origin=source)
        sideWalkPoint = getSideWalkPoint(newLine)
        if sideWalkPoint is not None:
            leftScanLines.append(newLine)
            leftSideWalkPoints.append(sideWalkPoint)
        else:
            break
    
    leftScanLines.reverse()
    leftSideWalkPoints.reverse()

    return leftScanLines + rightScanLines, leftSideWalkPoints + rightSideWalkPoints
    

centerScanLine = makeCenterScanLine(initialLocaltion, goalLocation)
# visualizer.drawShapelyLine(centerScanLine)
scanLines, sideWalkPoints = getScanLinesAndSidewalkPoints(centerScanLine)
    

# scanLines = []
# for i in range(4, 0, -1):
#     angle = -10 * i
#     scanLines.append(rotate(centerScanLine, angle, origin=source))

# scanLines.append(centerScanLine)

# for i in range(1, 5):
#     angle = 10 * i
#     scanLines.append(rotate(centerScanLine, angle, origin=source))


# visualizer.drawLine(initialLocaltion, goalLocation)
# visualizer.drawLine(carla.Location(scanLine.coords[0][0], scanLine.coords[0][1], 1), carla.Location(scanLine.coords[1][0], scanLine.coords[1][1], 1))

count = 0
for scanLine in scanLines: 
    count += 1
    visualizer.drawShapelyLine(scanLine, life_time=2.0, color=(50, count * 5, count * 5))


for sidewalkPoint in sideWalkPoints:
    visualizer.drawShaplyPoint(sidewalkPoint, color=(0, 100, 200), life_time=5.0)

# print(sideWalkPoints)
# draw envelope
envelope = Polygon([source, sideWalkPoints[0], sideWalkPoints[-1]])

visualizer.drawShapelyPolygon(envelope, color=(0, 100, 100, 100), life_time=10.0)

# now we need to validate the sidewalk points being on the same sidewalk (there are corner cases)

