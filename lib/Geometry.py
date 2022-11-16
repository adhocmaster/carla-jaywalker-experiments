import carla
import copy
import math
from shapely.geometry import Point, LineString, Polygon
from shapely.affinity import scale, rotate
from typing import List, Tuple

class Geometry: 

    @staticmethod
    def getGlobalYaw(subject: carla.Vector3D): 
        """Returns rotation around Z"""
        return math.atan2(subject.y, subject.x)

    
    @staticmethod
    def changeCartesianCenter(subject: carla.Vector3D, center: carla.Vector3D, centerDirection: carla.Vector3D=None, centerRotation=None) -> carla.Vector3D:

        clone = subject - center 
        # clone = carla.Vector3D(x=subject.x, y=subject.y, z=subject.z)
        # clone.x -= center.x
        # clone.y -= center.y
        # clone.z -= center.z

        if centerDirection is not None:
            angle = -Geometry.getGlobalYaw(centerDirection)
            clone = Geometry.rotateAroundZ(clone, angle)
        elif centerRotation is not None:
            angle = -centerRotation
            clone = Geometry.rotateAroundZ(clone, angle)


        return clone
    

    @staticmethod
    def rotateAroundZ(subject: carla.Vector3D, angle) -> carla.Vector3D:
        """_summary_

        Args:
            subject (carla.Vector3D): _description_
            angle (_type_): If we are transforming to another reference frame, angle should negated 

        Returns:
            carla.Vector3D: _description_
        """

        clone = carla.Vector3D(x=subject.x, y=subject.y, z=subject.z)
        clone.x = subject.x * math.cos(angle) - subject.y * math.sin(angle)
        clone.y = subject.x * math.sin(angle) + subject.y * math.cos(angle)
        
        return clone

    
    @staticmethod
    def distanceTuples(point1, point2):
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

    @staticmethod
    def locationToPoint(location: carla.Location) -> Point:
        return Point(location.x, location.y)
    
    @staticmethod 
    def pointtoLocation(point: Point) -> carla.Location:
        return carla.Location(point[0], point[1], 0.1)


    #region scanning for sidewalks

    @staticmethod
    def findClosestSidewalkPointOnTheOtherSide(source: carla.Location) -> carla.Location:
        pass # TODO

    @staticmethod
    def makeCenterScanLine(source: carla.Location, dest: carla.Location) -> LineString:

        s = (source.x, source.y)
        d = (dest.x, dest.y)
        yAxis = LineString([s, d])
        centerScanLine = scale(yAxis, xfact=1.5, yfact=1.5, origin=s)
        return centerScanLine


    @staticmethod
    def getSideWalkPointOnScanLine(world:carla.World, scanLine: LineString) -> Point:
        """gets a point on the sidewalk 1 meter inside from the edge of detection

        Args:
            world (carla.World): _description_
            scanLine (LineString): _description_

        Returns:
            Point: _description_
        """
        
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


    @staticmethod
    def getScanLinesAndSidewalkPoints(world:carla.World, centerScanLine: LineString) -> Tuple[List[LineString], List[Point]]:
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
            newLine = rotate(centerScanLine, angle, origin=centerScanLine.coords[0])
            sideWalkPoint = Geometry.getSideWalkPointOnScanLine(world, newLine)
            if sideWalkPoint is not None:
                rightScanLines.append(newLine)
                rightSideWalkPoints.append(sideWalkPoint)
            else:
                break
        
        
        leftScanLines = []
        leftSideWalkPoints = []
        for i in range(1, 10):
            angle = -10 * i
            newLine = rotate(centerScanLine, angle, origin=centerScanLine.coords[0])
            sideWalkPoint = Geometry.getSideWalkPointOnScanLine(world, newLine)
            if sideWalkPoint is not None:
                leftScanLines.append(newLine)
                leftSideWalkPoints.append(sideWalkPoint)
            else:
                break
        
        leftScanLines.reverse()
        leftSideWalkPoints.reverse()

        return leftScanLines + rightScanLines, leftSideWalkPoints + rightSideWalkPoints

    #endregion


    
